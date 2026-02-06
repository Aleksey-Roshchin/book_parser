import parse_books as pb

if __name__ == "__main__":
    pb.parse_book(
        "https://loveread.ec/read_book.php?id=115958&p=1",
        "./books",
        log=print,
        delay=1.2
    )