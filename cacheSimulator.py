import math
from collections import deque
from L2Cache import L2Cache

# 대입하는 주소들
addresses = [4, 8, 20, 24, 28, 36, 44, 20, 24, 28, 36, 40, 44, 68,
             72, 92, 96, 100, 104, 108, 112, 100, 112, 116, 120, 128, 140]
# 메모리의 크기
address_size = 16
#instruction_size = 32

block_size = 4  # in bytes
number_of_rows = 8  # must be multiple of 2

# set의 개수.
# number_of_sets = 4  # must be multiple of 2 (r)
ways = 1  # can be any number (n)
# max number of bits all fields can take, tag, valid, LRU, data, etc.
max_storage_bits = 400
# Set Associative requires LRU for each way ceil(lg n)
# Fully Associative requires LRU for each row ceil(lg r)


miss_cost = 18 + (3 * block_size)
hit_cost = 1
l2hit_cost = 6


def checkDirectMap():
    row_bits = math.ceil(math.log(number_of_rows, 2))  # 라인에 배정되는 캐시
    index_bits = math.ceil(math.log(block_size, 2))  # 워드에 배정되는 캐시
    tag_bits = address_size - row_bits - index_bits
    valid_bits = 1
    row_size = tag_bits + (8 * block_size) + valid_bits
    table_size = row_size * number_of_rows
    if table_size > max_storage_bits:
        print("Cache is too large, change your numbers: " +
              str(table_size) + "/" + str(max_storage_bits))
    else:
        print("Cache is within size constraints: " +
              str(table_size) + "/" + str(max_storage_bits))


def checkSetAssociative():
    row_bits = math.ceil(math.log(number_of_rows, 2))
    # row_bits = line
    index_bits = math.ceil(math.log(block_size, 2))
    # index_bits : word
    tag_bits = address_size - row_bits - index_bits
    valid_bits = 1
    LRU_bits = math.ceil(math.log(ways, 2))
    row_size = (tag_bits + (8 * block_size) + valid_bits + LRU_bits) * ways
    table_size = row_size * number_of_rows
    if table_size > max_storage_bits:
        print("Cache is too large, change your numbers: " + str(table_size))
    else:
        print("Cache is within size constraints: " +
              str(table_size) + "/" + str(max_storage_bits))


def checkFullyAssociative():
    index_bits = math.ceil(math.log(block_size, 2))
    tag_bits = address_size - index_bits
    LRU_bits = math.ceil(math.log(number_of_rows, 2))
    valid_bits = 1
    row_size = tag_bits + (8 * block_size) + valid_bits + LRU_bits
    table_size = row_size * number_of_rows
    if table_size > max_storage_bits:
        print("Cache is too large, change your numbers: " + str(table_size))
    else:
        print("Cache is within size constraints: " +
              str(table_size) + "/" + str(max_storage_bits))


def missTime():
    print("A cache miss will cost you: " + str(miss_cost) + " cycles")
    print(f"l2 cache hit will cost you {l2hit_cost} cycles")


def simulateDirectMap():
    l2cache = L2Cache(number_of_rows)

    tags = [0] * number_of_rows
    valid = [0] * number_of_rows
    miss_count = 0  # l1 l2 다 없을 때
    l1_miss_count = 0  # l1 없는데 l2는 있을 때
    total_instructions = 0
    for i in range(0, 3):
        for addr in addresses:
            #  addr = addresses[i]
            offset = addr % block_size
            row = (addr // block_size) % number_of_rows
            tag = addr // (block_size * number_of_rows)
            print("Address: " + str(addr) + ", tag: " + str(tag) +
                  ", row: " + str(row) + ", offset: " + str(offset), end="\t")
            if valid[int(row)] == 0:  # 데이터가 없는 경우. L1 캐시와 L2 캐시 모두에 써야 한다.
                print("placing item")
                valid[int(row)] = 1
                tags[int(row)] = tag
                l2cache.act(tag, i)
            # 데이터는 있는데 태그가 맞지 않는 경우. conflict miss.
            elif tag != tags[int(row)]:
                # 만약 L2 캐시 뒤져서 있다면 사용. 없다면 기존 그대로.
                l2miss = l2cache.act(tag, i)
                tags[int(row)] = tag
                print("Cache Miss - updating row " + str(row))
                if i > 0:
                    if l2miss:
                        miss_count += 1
                    else:
                        l1_miss_count += 1

            else:  # 데이터 발견.
                print("Cache Hit on row " + str(row))
            if i > 0:
                total_instructions += 1

        print("END OF CYCLE " + str(i))
        print("")

    print("row\tvalid\ttag")
    for j in range(0, number_of_rows):
        print(str(j) + "\t" + str(valid[j]) + "\t" + str(tags[j]))
    cpi = (hit_cost * (total_instructions - l1_miss_count - miss_count)  # l1에서 hit
           + l2hit_cost * l1_miss_count  # l2에서 hit
           + miss_cost * miss_count) / total_instructions  # 전체 miss
    print("CPI: " + str(cpi))
    print("Simulation complete")


def simulateSetAssociative():
    l2cache = L2Cache(number_of_rows)

    tags = [[-1 for i in range(0, ways)] for i in range(0, number_of_rows)]
    valid = [[0 for i in range(0, ways)] for i in range(0, number_of_rows)]
    LRU = [deque() for i in range(0, number_of_rows)]

    miss_count = 0
    l1_miss_count = 0
    total_instructions = 0

    for i in range(0, 3):
        for addr in addresses:
            offset = addr % block_size
            row = (addr // block_size) % number_of_rows
            tag = addr // (block_size * number_of_rows)
            print("Address: " + str(addr) + ", tag: " + str(tag) +
                  ", row: " + str(row) + ", offset: " + str(offset), end="\t")
            flag = False  # flag false이면 miss. flag True이면 처음으로 삽입.
            # if our tag is in our row and its valid
            if (tag in tags[row]) and (valid[row][tags[row].index(tag)]):
                print("Cache Hit")
                if i > 0:
                    total_instructions += 1
                continue  # go to the next address, we found this one
            # 태그가 존재하지 않는 경우.

            for j in range(0, ways):  # if we couldn't find it, see if there is an open spot
                if valid[row][j] == 0:  # valid하지 않은 경우
                    tags[row][j] = tag  # 값 설정

                    l2cache.act(tag, i)  # l2 캐시 처리

                    if j in LRU[row]:
                        LRU[row].remove(j)
                    LRU[row].append(j)  # LRU 처리

                    valid[row][j] = 1
                    flag = True  # 첫번째 추가는 miss로 안치는 것으로 보임.
                    print("added item for the first time")
                    break
            if flag == False:  # The tag was wrong
                leastUsedWay = LRU[row].popleft()
                tags[row][leastUsedWay] = tag
                l2miss = l2cache.act(tag, i)  # l2 캐시 처리

                if i > 0:
                    if l2miss:
                        miss_count += 1  # 둘 다 miss면 miss
                    else:
                        l1_miss_count += 1  # l1만 미스면 이거

                LRU[row].append(leastUsedWay)
                print("Cache Miss - updating entry")

            if i > 0:
                total_instructions += 1
        print("END OF CYCLE: " + str(i))
        print("")

    print("row\tvalid\ttag\t|\tvalid\ttag")
    for j in range(0, number_of_rows):
        print(str(j) + "\t\t", end="")
        for k in range(0, ways):
            print(str(valid[j][k]) + "\t" + str(tags[j][k]) + "\t|\t", end="")
        print("")

    cpi = (hit_cost * (total_instructions - l1_miss_count - miss_count)  # l1에서 hit
           + l2hit_cost * l1_miss_count  # l2에서 hit
           + miss_cost * miss_count) / total_instructions  # 전체 miss
    print("CPI: " + str(cpi))
    print("Simulation Complete")


def simulateFullyAssociative():
    l2cache = L2Cache(number_of_rows)

    tags = [-1] * number_of_rows
    valid = [0] * number_of_rows
    LRU = deque()

    miss_count = 0
    l1_miss_count = 0
    total_instructions = 0

    for i in range(0, 3):
        for addr in addresses:
            offset = addr % block_size
            tag = addr // (block_size)
            print("Address: " + str(addr) + ", tag: " +
                  str(tag) + ", offset: " + str(offset), end="\t")

            # see if tag is in table - hit
            if tag in tags:  # hit 한 경우.
                location = tags.index(tag)
                if location in LRU:
                    LRU.remove(location)
                LRU.append(location)
                print("Cache Hit")

            # see if there is an invalid row, - miss, add it
            elif 0 in valid:  # hit 아니고 값 설정 안한 부분 있는 경우
                location = valid.index(0)
                l2miss = l2cache.act(tag, i)  # l2 캐시 처리
                tags[location] = tag
                valid[location] = 1
                if i > 0:
                    if l2miss:
                        print("All MISS!")
                        miss_count += 1  # 둘 다 miss면 miss
                    else:
                        print("l2 hit!")
                        l1_miss_count += 1  # l1만 미스면 이거
                if location in LRU:
                    LRU.remove(location)
                    print("THIS SHOULDNT HAPPEN!!!!!!!!!!!!")
                LRU.append(location)
                print("Cache Miss - adding to empty row")

            # else, find least recently used and update - miss
            else:  # 꽉 차있는 경우
                # l2 캐시 처리 = l2 뒤져서 해당 데이터 있는지 먼저 찾기
                l2miss = l2cache.act(tag, i)
                leastUsedLoc = LRU.popleft()
                tags[leastUsedLoc] = tag

                if i > 0:
                    if l2miss:
                        print("All MISS!")
                        miss_count += 1  # 둘 다 miss면 miss
                    else:
                        print("l2 hit!")
                        l1_miss_count += 1  # l1만 미스면 이거

                if leastUsedLoc in LRU:
                    LRU.remove(leastUsedLoc)
                    print("THIS SHOULDNT HAPPEN!!!!!!!!!!!!")
                LRU.append(leastUsedLoc)
                print("Cache Miss - replacing row")

            if i > 0:
                total_instructions += 1

    print("row\tvalid\ttag")
    print(l1_miss_count)
    print(miss_count)
    for j in range(0, number_of_rows):
        print(str(j) + "\t" + str(valid[j]) + "\t" + str(tags[j]))
    cpi = (hit_cost * (total_instructions - l1_miss_count - miss_count)  # l1에서 hit
           + l2hit_cost * l1_miss_count  # l2에서 hit
           + miss_cost * miss_count) / total_instructions  # 전체 miss
    print("CPI: " + str(cpi))
    print("SIMULATION COMPLETE")


def main():
    # checkDirectMap()
    # checkSetAssociative()
    checkFullyAssociative()

    missTime()

    # simulateDirectMap()
    # simulateSetAssociative()
    simulateFullyAssociative()


if __name__ == "__main__":
    main()
