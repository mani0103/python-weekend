import fire


def run(src, dst, date, cheapest, shortest, is_return):
    print(src, dst, cheapest, shortest, is_return)


if __name__ == '__main__':
    fire.Fire(run)