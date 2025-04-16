import asyncio
import time
from dataclasses import dataclass

import aiohttp
import numpy as np
import pandas as pd
import requests

URL = "https://010kzrsh75.execute-api.us-west-2.amazonaws.com/prod/"
HEALTHCHECK = URL + "healthcheck"


def test_single_request_healthcheck():
    """Test the single response endpoint."""
    response = requests.get(HEALTHCHECK)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_async_request_healthcheck():
    """Test the async response endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(HEALTHCHECK) as response:
            assert response.status == 200
            assert await response.json() == {"status": "ok"}


@dataclass
class ResponseInfo:
    """Class to hold response information."""

    status_code: int
    response_time: float
    retry_count: int = 0


async def timed_response(session: aiohttp.ClientSession, url: str) -> ResponseInfo:
    """Get the response time for a single request."""
    t0 = time.perf_counter()

    async with session.get(url) as response:
        status = response.status

    t1 = time.perf_counter()
    return ResponseInfo(status_code=status, response_time=t1 - t0)


async def retry_timed_response(session: aiohttp.ClientSession, url: str) -> ResponseInfo:
    """Get the response time with retry strategy for a single request."""
    backoff_times = [0.1, 1, 5, None]  # Backoff times in seconds
    response_info = ResponseInfo(status_code=0, response_time=0)
    retries = 0
    for backoff in backoff_times:
        response_info = await timed_response(session, url)
        response_info.retry_count = retries
        retries += 1
        if response_info.status_code == 200:
            return response_info
        if backoff is None:
            break
        await asyncio.sleep(backoff)
    return response_info


async def run_requests(num_requests: int, retry: bool = False):
    """Run multiple requests and collect response data."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            if retry:
                tasks.append(retry_timed_response(session, HEALTHCHECK))
            else:
                tasks.append(timed_response(session, HEALTHCHECK))
        responses: list[ResponseInfo] = await asyncio.gather(*tasks)
    return responses


def analyze_responses(responses: list[ResponseInfo]):
    """Analyze response data and print statistics."""
    # Collect data in a pandas DataFrame
    data = {
        "Status Code": [response.status_code for response in responses],
        "Response Time": [response.response_time for response in responses],
        "Retry Count": [response.retry_count for response in responses],
    }
    df = pd.DataFrame(data)
    df.sort_values(by="Response Time", ascending=True, inplace=True)

    # Print the DataFrame
    print("Response Data:")
    print(df.head(10))
    print("...")
    print(df.tail(10))

    # Group by status code and calculate statistics
    grouped = (
        df.groupby("Status Code")
        .agg(
            Mean_Response_Time=("Response Time", "mean"),
            Std_Response_Time=("Response Time", "std"),
            Count=("Response Time", "count"),
        )
        .reset_index()
    )

    # Print the grouped DataFrame
    print("\nGrouped Response Data by Status Code:")
    print(grouped)

    # Calculate quantiles for each status code
    quantiles = [0.05, 0.2, 0.5, 0.8, 0.95]
    quantile_df = df.groupby("Status Code")["Response Time"].quantile(np.array(quantiles)).unstack()
    quantile_df.columns = [f"{int(q * 100)}th Quantile" for q in quantiles]
    quantile_df.reset_index(inplace=True)

    # Print the quantile DataFrame
    print("\nQuantiles by Status Code:")
    print(quantile_df)
    return df

def save_df(df: pd.DataFrame, filename: str):
    """Save the DataFrame to a CSV file."""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Test without retry
async def test_time_100_healthchecks():
    """Test the async response endpoint without retry."""
    print("\n\nStarting async requests without retry...")
    responses = await run_requests(100, retry=False)
    df = analyze_responses(responses)
    save_df(df, "response_data_no_retry.csv")


# Test with retry
async def test_time_100_healthchecks_with_retry():
    """Test the async response endpoint with retry strategy."""
    print("\n\nStarting async requests with retry...")
    responses = await run_requests(100, retry=True)
    df = analyze_responses(responses)
    save_df(df, "response_data_with_retry.csv")
