from human_requests import Session
from human_requests.impersonation import ImpersonationConfig, Policy
from human_requests.abstraction.http import HttpMethod
import asyncio
import json
import pprint

async def main():
    # Session initialization
    s = Session(headless=False,  # False is useful for debugging
                browser="firefox",  # camoufox is best for large-scale requests, but may be less stable
                # For non-camoufox (it already supports this by default), hides some automation signatures
                # Recommended to enable for standard Playwright browsers
                playwright_stealth=False,
                spoof=ImpersonationConfig())

    await s.start()

    # Warm up the session (cookies + default local storage)
    async with s.goto_page("https://5ka.ru/", wait_until="networkidle") as page:
        await page.wait_for_selector(selector="next-route-announcer", state="attached")
        #await asyncio.sleep(9999999)

    # Parse the default store location
    default_store_location = json.loads(s.local_storage["https://5ka.ru"]["DeliveryPanelStore"])
    sap_code = default_store_location['selectedAddress']['sapCode']

    headers = {  # Static headers, without them you’ll get a 400
        "Origin": "https://5ka.ru",
        "X-PLATFORM": "webapp",
        # Device ID saved by site JS during warm-up
        "X-DEVICE-ID": s.local_storage["https://5ka.ru"]["deviceId"],
        "X-APP-VERSION": "0.1.1.dev"
    }
    
    #print(headers)
    #print(sap_code)

    # Cookies are attached automatically
    resp = await s.request(
        HttpMethod.GET,  # Equivalent of "GET"
        # Fetch the default store from local storage
        f"https://5d.5ka.ru/api/catalog/v2/stores/{sap_code}/categories?mode=delivery&include_subcategories=1&include_restrict=true",
        headers=headers
    )

    # If while parsing the response you encounter, for example:
    # a JS challenge that must be solved to get the data,
    # you can render the result directly in the browser (without a duplicate request).
    # Advantage: no duplicate requests (less suspicious, saves rate limit).

    # async with resp.render() as p:
    #     await p.wait_for_load_state("networkidle")
    #     print(await p.content())

    # Don’t forget to close the session (in a `with` context it would close automatically)
    await s.close()

    print(resp.status_code)
    print(resp.request.headers)

    # Verify result
    assert resp.status_code == 200

    # Parse body
    json_result = json.loads(resp.body)

    # Process further as you wish
    names = []
    for element in json_result:
        names.append(element["name"])

    from pprint import pprint
    pprint(names)

if __name__ == "__main__":
    asyncio.run(main())