from collections import deque

class L2Cache:
    """
    fully associative로 운영되는 L2 캐시. 크기는 L1 캐시의 2배.
    """

    def __init__(self, number_of_rows: int):
        self.tags = [0 for _ in range(number_of_rows * 2)]
        self.valid = self.tags.copy()  # 태그의 모습과 동일하게 정의된다.
        self.LRU = deque()  # L2 캐시에서도 LRU 사용

    def write(self, tag):
        """
        데이터를 쓰는 동작. 첫번째 라운드 이후라면 miss 발생할 수 있다.
        만약 이미 존재한다면 hit
        아니면 miss
        그러나, L1 캐시 입장에서는 L2 안에 존재하는지 여부만 중요하다.
        """

        # 대응되는 태그가 존재하는 경우 -> 데이터가 L2 캐시 내에 있는 경우
        if tag in self.tags:
            location = self.tags.index(tag)
            if location in self.LRU:
                self.LRU.remove(location)  # 기존에 사용되었던 기록 삭제하고
            self.LRU.append(location)  # 최근에 사용된 것이라고 바꿈.
            # 읽기 과정에서 검증하므로 이 코드가 실행될 일은 없어야 함.

        # L2 캐시에서 비어있는 공간이 있는 경우 -> 빈 공간에 쓰기
        elif 0 in self.valid:
            location = self.valid.index(0)
            self.valid[location] = 1  # 해당 공간 valid 처리
            self.tags[location] = tag  # 해당 공간 태그 넣기
            self.LRU.append(location)  # 최근에 사용된 위치라고 LRU에 추가
        # 태그는 없지만 모든 공간이 valid. L2 캐시가 꽉 찬 경우
        else:
            leastUsedLoc = self.LRU.popleft()  # 사용한지 가장 오래된 값을 제거
            self.tags[leastUsedLoc] = tag  # 해당 위치의 태그 값을 수정
            # 오래된 위치 제거했으니까, LRU 배열 상에 없음. 그냥 삽입만 하면 됨.
            self.LRU.append(leastUsedLoc)  # LRU 배열 상에 삽입.

    def act(self, tag, round):
        """
        데이터를 읽되, 없으면 쓰는 동작.
        miss로 처리해야 하면 true, 아니면 false을 반환한다.
        miss로 처리되는 조건
        1. 첫번째 라운드 이후에
        2. hit가 아닌 경우
        """
        if tag in self.tags:  # hit 한 경우. 무조건 false 반환
            location = self.tags.index(tag)
            if location in self.LRU:
                self.LRU.remove(location)  # 기존에 사용되었던 기록 삭제하고
            self.LRU.append(location)  # 최근에 사용된 것이라고 바꿈.
            return False  # 초기화 과정이든 아니든 무조건 false 반환하게 된다.

        # miss인 경우. round > 0이라면 true 반환.
        else:
            self.write(tag)
            if round > 0:
                return True  # miss로 처리되는 경우