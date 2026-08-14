from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Program generation: structured output against a fixed exercise context, but
# it does require real judgment - matching injuries/constraints against
# exercise selection isn't pure extraction. "low" keeps a real reasoning
# budget for that while staying far faster than the unset "medium" default
# that was driving the ~1.4 minute generation time.
#
# gpt-5.4-mini defaults reasoning_effort to "none" itself (vs base gpt-5-mini's
# "medium"), suggesting it's tuned to be capable without leaning on deliberation
# - "low" here is a deliberate bump up from that default for the injury/
# constraint judgment this task needs, not a fight against the model's grain.
#
# No `temperature` set: GPT-5-family models only honor temperature when
# reasoning_effort="none" - at "low" it's silently ignored, so there's no
# reason to carry it.
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    reasoning_effort="low",
)

# Coach chat agent: reasons across up to 10 tools and up to 3 loop iterations,
# interpreting someone's actual training situation. Same reasoning_effort as
# program generation - both need real judgment, neither needs "medium".
#
# use_responses_api=True is required here: this agent uses bind_tools() for
# function calling, and gpt-5.4-mini rejects the combination of function tools
# + reasoning_effort on the Chat Completions endpoint (400: "Function tools
# with reasoning_effort are not supported ... use /v1/responses or set
# reasoning_effort to 'none'"). The Responses API supports both together.
# (Program generation above doesn't need this - with_structured_output()
# defaults to json_schema mode, not function calling, so it isn't affected.)
coach_llm = ChatOpenAI(
    model="gpt-5.4-mini",
    reasoning_effort="medium",
    use_responses_api=True,
)