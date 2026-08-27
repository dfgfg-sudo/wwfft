import re
async def main(args: Args) -> Output:
    input_text = args.params.get('input', '')
    texts = re.split(r"\n", input_text)
    texts = [t for t in texts if t.strip() != ""]
    return {"output1": "\n".join(texts[:-1]), "output2": texts[-1] if texts else ""}