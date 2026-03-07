from __future__ import annotations

from typing import Any

import aiohttp
import pytest
from human_requests import (
    autotest_data,
    autotest_depends_on,
    autotest_hook,
    autotest_params,
)
from human_requests.abstraction import Proxy
from human_requests.autotest import (
    AutotestCallContext,
    AutotestContext,
    AutotestDataContext,
)
from PIL import Image

from pyaterochka_api.endpoints.catalog import ClassCatalog, ProductService
from pyaterochka_api.endpoints.geolocation import ClassGeolocation


def _extract_sap_code(store_data: dict[str, Any]) -> str:
    try:
        sap_code = store_data["selectedStore"]["sapCode"]
    except (KeyError, TypeError):
        pytest.fail("delivery_panel_store did not return selectedStore.sapCode.")

    if not isinstance(sap_code, str) or not sap_code:
        pytest.fail("delivery_panel_store returned invalid sapCode.")
    return sap_code


async def _resolve_sap_code(ctx: AutotestCallContext | AutotestDataContext) -> str:
    cached = ctx.state.get("autotest_sap_code")
    if isinstance(cached, str) and cached:
        return cached

    store_data = await ctx.api.delivery_panel_store()
    sap_code = _extract_sap_code(store_data)
    ctx.state["autotest_sap_code"] = sap_code
    return sap_code


def _require_state_str(ctx: AutotestCallContext, key: str) -> str:
    value = ctx.state.get(key)
    if isinstance(value, str) and value:
        return value
    pytest.fail(f"Missing required state value: {key}.")


@autotest_data(name="PyaterochkaAPI.delivery_panel_store")
async def _delivery_panel_store_data(ctx: AutotestDataContext) -> dict[str, Any]:
    data = await ctx.api.delivery_panel_store()
    ctx.state["autotest_sap_code"] = _extract_sap_code(data)
    return data


@autotest_data(name="PyaterochkaAPI.device_id")
async def _device_id_data(ctx: AutotestDataContext) -> str:
    return await ctx.api.device_id()


@autotest_params(target=ClassCatalog.tree)
async def _tree_params(ctx: AutotestCallContext) -> dict[str, str]:
    return {"sap_code_store_id": await _resolve_sap_code(ctx)}


@autotest_hook(target=ClassCatalog.tree)
def _capture_first_category(
    resp: Any,
    data: list[dict[str, Any]],
    ctx: AutotestContext,
) -> None:
    del resp
    if not isinstance(data, list) or not data:
        pytest.fail("Catalog.tree returned empty data.")

    first_category = data[0]
    category_id = first_category.get("id")
    if isinstance(category_id, int):
        category_id = str(category_id)
    if not isinstance(category_id, str) or not category_id:
        pytest.fail("Catalog.tree did not return valid category id.")

    ctx.state["autotest_first_category_id"] = category_id


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.tree_extended)
@autotest_params(target=ClassCatalog.products_list)
@autotest_params(target=ClassCatalog.products_line)
def _category_params(ctx: AutotestCallContext) -> dict[str, str]:
    return {
        "sap_code_store_id": _require_state_str(ctx, "autotest_sap_code"),
        "category_id": _require_state_str(ctx, "autotest_first_category_id"),
    }


@autotest_params(target=ClassCatalog.search)
async def _catalog_search_params(ctx: AutotestCallContext) -> dict[str, str]:
    return {
        "sap_code_store_id": await _resolve_sap_code(ctx),
        "query": "кола",
    }


@autotest_hook(target=ClassCatalog.products_list)
def _capture_product_plu(
    resp: Any,
    data: dict[str, Any],
    ctx: AutotestContext,
) -> None:
    del resp
    if not isinstance(data, dict):
        pytest.fail("Catalog.products_list returned invalid payload.")

    products = data.get("products")
    if not isinstance(products, list) or not products:
        pytest.fail("Catalog.products_list returned empty products.")

    product_plu = products[0].get("plu")
    if not isinstance(product_plu, (str, int)):
        pytest.fail("Catalog.products_list did not return valid product plu.")

    ctx.state["autotest_product_plu"] = str(product_plu)


@autotest_depends_on(ClassCatalog.products_list)
@autotest_params(target=ProductService.info)
def _product_info_params(ctx: AutotestCallContext) -> dict[str, str]:
    return {
        "sap_code_store_id": _require_state_str(ctx, "autotest_sap_code"),
        "plu_id": _require_state_str(ctx, "autotest_product_plu"),
    }


@autotest_params(target=ClassGeolocation.suggest)
def _suggest_params(ctx: AutotestCallContext) -> dict[str, str]:
    del ctx
    return {"query": "армавир"}


@autotest_hook(target=ClassGeolocation.geocode)
def _capture_geoposition(
    resp: Any,
    data: dict[str, Any],
    ctx: AutotestContext,
) -> None:
    del resp
    try:
        pos = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
            "Point"
        ]["pos"]
    except (KeyError, IndexError, TypeError):
        pytest.fail("Geolocation.geocode did not return geoposition.")

    if not isinstance(pos, str):
        pytest.fail("Geolocation.geocode returned non-string geoposition.")

    try:
        longitude_raw, latitude_raw = pos.split(" ", maxsplit=1)
        longitude = float(longitude_raw)
        latitude = float(latitude_raw)
    except (ValueError, TypeError):
        pytest.fail("Geolocation.geocode returned invalid geoposition format.")

    ctx.state["autotest_longitude"] = longitude
    ctx.state["autotest_latitude"] = latitude


@autotest_depends_on(ClassGeolocation.geocode)
@autotest_params(target=ClassGeolocation.find_store)
def _find_store_params(ctx: AutotestCallContext) -> dict[str, float]:
    longitude = ctx.state.get("autotest_longitude")
    latitude = ctx.state.get("autotest_latitude")
    if not isinstance(longitude, float) or not isinstance(latitude, float):
        pytest.fail("Geolocation.find_store depends on Geolocation.geocode.")

    return {"longitude": longitude, "latitude": latitude}


async def test_proxy_ip() -> None:
    proxy = Proxy.from_env()
    if not proxy:
        pytest.skip("Proxy not configured")

    proxy_str = proxy.as_str()
    proxy_without_auth = proxy.as_str(include_auth=False)
    if not proxy_str or not proxy_without_auth:
        pytest.skip("Proxy server is not configured")

    async with aiohttp.ClientSession() as session:
        async with session.get("http://httpbin.org/ip", proxy=proxy_str) as resp:
            ip = (await resp.json())["origin"]

    expected = proxy_without_auth.removeprefix("http://").removeprefix("https://")
    expected = expected.split(":", maxsplit=1)[0]
    assert ip == expected


async def test_download_image(api) -> None:
    store_data = await api.delivery_panel_store()
    sap_code = _extract_sap_code(store_data)

    tree_data = (await api.Catalog.tree(sap_code_store_id=sap_code)).json()
    if not isinstance(tree_data, list) or not tree_data:
        pytest.fail("Catalog.tree returned empty data.")

    categories = tree_data[0].get("categories", [])
    if not isinstance(categories, list) or not categories:
        pytest.skip("No nested category with image_link was found.")

    image_link = categories[0].get("image_link")
    if not isinstance(image_link, str) or not image_link:
        pytest.skip("No image_link in first category.")

    resp = await api.General.download_image(image_link)
    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")
