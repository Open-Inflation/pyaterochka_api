from standard_open_inflation_package import BaseAPI
from standard_open_inflation_package.handler import Handler, HandlerSearchFailed, HandlerSearchSuccess, ExpectedContentType
from pprint import pprint


async def main():
    browser = BaseAPI(debug=True, timeout=20.0, trust_env=True)
    page = await browser.new_page()

    result = await page.direct_fetch("https://5ka.ru/api/public/v1/news/", handlers=Handler.NONE())

    print(type(result[0]).__name__, flush=True)
    if isinstance(result[0], HandlerSearchFailed):
        for r in result[0].rejected_responses:
            print(f"{r.status} | {r.request_headers.get('content-type', 'unknown')} | {type(r.response).__name__}", flush=True)
            #print()
            #pprint(r.request_headers)
            #print()
            #pprint(r.response_headers)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())