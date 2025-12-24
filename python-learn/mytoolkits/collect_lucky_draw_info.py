from tqdm import tqdm


def find_ups(self, ups=[]):
    for mid in tqdm(ups):
        self.findauthor(mid, down_pics=True, down_loc=self.user_dy_path, db_path=self.db_path)


if __name__ == '__main__':
    pass