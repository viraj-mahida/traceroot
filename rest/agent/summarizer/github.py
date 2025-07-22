from openai import AsyncOpenAI
from pydantic import BaseModel, Field

GITHUB_PROMPT = (
    "You are a helpful assistant that can summarize whether "
    "the user question is related to either creating an issue "
    "or a PR. If the user question is related to either creating an issue "
    "or a PR, please return True for the corresponding field. "
    "Otherwise, please return False for both fields. Please only return "
    "True or False for one field ONLY IF THE USER QUESTION IS "
    "100% RELATED TO EITHER CREATING AN ISSUE OR A PR. Otherwise, "
    "please return False for both fields.")


class GithubRelatedOutput(BaseModel):
    r"""Github related output.
    """
    is_github_issue: bool = Field(
        description=("Whether the user question is related to either "
                     "creating an issue or a PR."))
    is_github_pr: bool = Field(
        description=("Whether the user question is related to either "
                     "creating an issue or a PR."))


async def get_github_related(
    user_message: str,
    client: AsyncOpenAI,
    openai_token: str | None = None,
    model: str = "gpt-4o-mini",
) -> GithubRelatedOutput:
    if openai_token is not None:
        client = AsyncOpenAI(api_key=openai_token)
    response = await client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": GITHUB_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            },
        ],
        text_format=GithubRelatedOutput,
        temperature=0.0,
    )
    return response.output[0].content[0].parsed
