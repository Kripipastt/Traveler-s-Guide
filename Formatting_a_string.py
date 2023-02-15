def format_text_block(text, frame_width):
    answer = []
    x = 0
    strok = ""
    for i in text:
        strok += i
        x += 1
        if x >= frame_width:
            answer.append(strok.strip() + "\n")
            strok = ""
            x = 0
    if strok:
        answer.append(strok.strip())
    return "".join(answer)


def main():
    print(format_text_block("пн 10:00–18:00; вт 10:00–21:00; ср 10:00–18:00; чт 10:00–21:00; пт,сб 10:00–18:00", 48))


if __name__ == '__main__':
    main()
