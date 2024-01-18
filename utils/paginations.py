from math import ceil

class Paginations:
    def __init__(self, total_records, current_page):
        self.records_per_page = 10  # 한 페이지 당 레코드 수
        self.pages_per_block = 5  # 한 블럭 당 페이지 수

        self.total_records = total_records  # 총 레코드 수
        self.current_page = current_page # 현재 페이지

        # 전체 페이지 수
        self.total_pages = self._calculate_total_pages()
        # 총 블럭 수
        self.total_blocks = ceil(self.total_pages / self.pages_per_block)
        # 현재 블럭
        self.current_block = self._calculate_current_block()
        # 현재 블럭 내 시작 페이지
        self.start_page = self._calculate_start_page()
        # 현재 블럭 내 끝 페이지
        self.end_page = self._calculate_end_page()
        # 현재 블럭 내 현재 페이지 시작 레코드 번호
        self.start_record_number = self._calculate_start_record_number()
        # 시작과 끝 페이지 리스트
        self.current_page_range = range(self.start_page, self.end_page + 1)

        # 현재 블럭 이전 페이지 번호
        self.previous_page = max(self.start_page - 1, 1)
        # 현재 블럭 이전 페이지 존재 여부
        self.has_previous_page = self.current_page > 1
        # 현재 블럭 다음 페이지 번호
        self.next_page = min(self.end_page + 1, self.total_pages)
        # 현재 블럭 다음 페이지 존재 여부
        self.has_next_page = self.current_block < self.total_blocks

        # 첫 페이지 번호
        self.first_page = 1
        # 첫 페이지 블럭 존재 여부
        self.has_previous_block = self.current_block > 1
        # 마지막 페이지 번호
        self.last_page = self.total_pages
        # 마지막 페이지 블럭 존재 여부
        self.has_next_block = self.current_block < self.total_blocks

    def _calculate_total_pages(self):
        return max(ceil(self.total_records / self.records_per_page), 1)

    def _calculate_current_block(self):
        return ceil(self.current_page / self.pages_per_block)

    def _calculate_start_page(self):
        return (self.current_block - 1) * self.pages_per_block + 1

    def _calculate_end_page(self):
        end_page = self.start_page + self.pages_per_block - 1
        return min(end_page, self.total_pages)
        # return end_page
    
    def _calculate_start_record_number(self):
        # 현재 페이지 번호와 페이지 당 레코드 수를 곱한 후 페이지 당 레코드 수를 빼고 1을 더하여 현재 페이지의 시작 레코드 번호를 계산
        return (self.current_page * self.records_per_page) - self.records_per_page

if __name__ == "__main__":
    # 예시 사용:
    total_records = [5, 12, 124,]  # 총 레코드 수
    current_pages_list = [[1], [1, 2,], [3, 7, 11,],]  # 현재 페이지 번호

    for total_record, current_pages in zip(total_records, current_pages_list):
        for current_page in current_pages :
            pagination = Paginations(total_record, current_page)

            print('총 레코드:{} / 총 블럭:{}, 현재:{} / 총 page:{}, 현재:{}'
                .format(pagination.total_records
                        ,pagination.total_blocks,pagination.current_block
                        ,pagination.total_pages ,pagination.current_page))
            
            page_tag_tuple = (pagination.has_previous_block, pagination.first_page
                            , pagination.has_previous_page, pagination.previous_page
                            , pagination.current_page_range
                            , pagination.has_next_page, pagination.next_page
                            , pagination.has_next_block, pagination.last_page)
            page_tag = "{0[0]},{0[1]} / {0[2]},{0[3]} | {0[4]} | {0[5]},{0[6]} / {0[7]}, {0[8]}".format(page_tag_tuple)
            print(page_tag)
            print('-'*20)
