import openai
openai.api_key = '...'    # Insert your own API key here

PROMPT = (
    'A student is asked to describe {}, '
    'and they give this answer: {}. '
    'Suppose you are to grade their answer, '
    'return 1 if they are correct '
    'and 0 if they are wrong.'
)


def ai_judge(term: str, defi: str) -> bool:
    refined_prompt = PROMPT.format(term, defi)
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages=[
          {'role': 'user',
           'content': refined_prompt}
      ]
    )
    ans = response['choices'][0]['message']['content']
    return ans == '1'
