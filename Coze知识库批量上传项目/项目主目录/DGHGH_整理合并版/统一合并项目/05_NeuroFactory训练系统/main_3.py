import re
async def main(args: Args) -> Output:
    params = args.params
    input_text = params['input']
    pattern = r"\n"
    texts = re.split(pattern, input_text)
    texts = [t for t in texts if t.strip() != ""]
    ret: Output = {
        "output1": "\n".join(texts[:-1]),
        "output2": texts[-1] if texts else ""
    }
    return ret