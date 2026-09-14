"""
03_hash.py — dict / set / Counter
===========================================================================
Day 4. 가장 자주 쓰이고, 가장 자주 "시간 초과를 푸는" 도구.

기억할 한 줄
    리스트에 `in` 을 쓰면 O(N), set/dict 는 O(1).
    "찾기"가 반복되는 문제에서 리스트를 set 으로 바꾸는 것만으로 통과한다.

언제 무엇을
    존재 확인 / 중복 제거      -> set
    키 -> 값 매핑              -> dict
    개수 세기                  -> Counter
    없는 키에 기본값           -> defaultdict
    양쪽 방향 조회             -> dict 두 개 (정방향, 역방향)

실행:  python 03_hash.py
===========================================================================
"""

from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# 1. 존재 확인 — set 으로 바꾸는 것만으로 통과하는 유형
# ---------------------------------------------------------------------------

def find_numbers(cards: list, queries: list) -> list:
    """숫자 카드 (백준 10815). 있으면 1, 없으면 0.

    cards 를 리스트로 두고 `in` 을 쓰면 O(N*M) 으로 시간 초과.
    set 으로 바꾸면 O(N+M).
    """
    table = set(cards)
    return [1 if q in table else 0 for q in queries]


def count_numbers(cards: list, queries: list) -> list:
    """숫자 카드 2 (백준 10816). 각 질의 숫자가 몇 장 있나.
    존재 여부가 아니라 개수 -> Counter.
    """
    counter = Counter(cards)
    return [counter[q] for q in queries]      # Counter 는 없는 키에 0 을 준다


def intersection_sorted(a: list, b: list) -> list:
    """듣보잡 (백준 1764). 두 목록에 모두 있는 것을 사전순으로.
    set 교집합 -> 정렬.
    """
    return sorted(set(a) & set(b))


# ---------------------------------------------------------------------------
# 2. 양방향 매핑 — 번호 <-> 이름 (백준 1620 포켓몬 마스터)
# ---------------------------------------------------------------------------

class TwoWayMap:
    """한쪽만 만들어두고 매번 뒤지면 O(N). 처음부터 두 개를 만든다."""

    def __init__(self, names: list):
        self.by_name = {name: i + 1 for i, name in enumerate(names)}
        self.by_index = {i + 1: name for i, name in enumerate(names)}

    def lookup(self, key: str):
        if key.isdigit():
            return self.by_index[int(key)]
        return self.by_name[key]


# ---------------------------------------------------------------------------
# 3. Counter 활용
# ---------------------------------------------------------------------------

def not_finished(participants: list, completions: list) -> str:
    """완주하지 못한 선수 (프로그래머스). 동명이인이 있다.

    Counter 끼리 빼면 개수 차이만 남는다. 이 한 줄이 이 문제의 정답.
    """
    remaining = Counter(participants) - Counter(completions)
    return list(remaining)[0]


def most_common_value(arr: list) -> int:
    """최빈값. 여러 개면 가장 작은 값.
    Counter.most_common() 은 개수 내림차순이지만 동률 순서는 보장되지 않으므로
    key 를 명시해서 정렬한다.
    """
    counter = Counter(arr)
    return min(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0]


def has_duplicate(arr: list) -> bool:
    """중복이 있는지. 길이 비교 한 줄."""
    return len(arr) != len(set(arr))


def group_by_length(words: list) -> dict:
    """defaultdict 로 그룹핑. 키가 없을 때 KeyError 를 신경 쓰지 않는다."""
    groups = defaultdict(list)
    for w in words:
        groups[len(w)].append(w)
    return dict(groups)


def anagram_groups(words: list) -> list:
    """애너그램 묶기. 정렬한 문자열을 키로 쓴다 — 해시 문제의 고전 패턴."""
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return [sorted(v) for v in sorted(groups.values(), key=lambda g: sorted(g))]


# ---------------------------------------------------------------------------
# 4. dict 로 O(N) 만드는 대표 패턴
# ---------------------------------------------------------------------------

def two_sum(nums: list, target: int):
    """두 수의 합. 인덱스 두 개를 반환. 없으면 None.

    2중 루프 O(N²) -> "필요한 짝을 dict 에 기억"해서 O(N).
    이 아이디어가 해시 문제의 핵심 전환이다.
    """
    seen = {}                       # 값 -> 인덱스
    for i, v in enumerate(nums):
        need = target - v
        if need in seen:
            return seen[need], i
        seen[v] = i
    return None


def first_unique_char(s: str) -> int:
    """처음으로 한 번만 나오는 문자의 인덱스. 없으면 -1."""
    counter = Counter(s)
    for i, ch in enumerate(s):
        if counter[ch] == 1:
            return i
    return -1


def longest_no_repeat(s: str) -> int:
    """중복 없는 가장 긴 부분 문자열 길이. 해시 + 슬라이딩 윈도우 결합.
    (04_two_pointer.py 와 이어지는 유형)
    """
    last = {}                       # 문자 -> 마지막 등장 인덱스
    start = 0
    best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1    # 중복이 생기면 그 다음 칸으로 왼쪽 경계를 민다
        last[ch] = i
        best = max(best, i - start + 1)
    return best


def clothes_combination(clothes: list) -> int:
    """위장 (프로그래머스). 종류별 개수를 곱하고, 각 종류는 '안 입기'도 가능.
    (개수+1) 을 전부 곱한 뒤 전부 안 입는 1가지를 뺀다.
    """
    kinds = defaultdict(int)
    for _name, kind in clothes:
        kinds[kind] += 1
    result = 1
    for cnt in kinds.values():
        result *= (cnt + 1)
    return result - 1


# ---------------------------------------------------------------------------
# 5. set 연산 정리
# ---------------------------------------------------------------------------

def set_ops(a: list, b: list) -> dict:
    sa, sb = set(a), set(b)
    return {
        "union": sorted(sa | sb),
        "intersection": sorted(sa & sb),
        "difference": sorted(sa - sb),
        "symmetric": sorted(sa ^ sb),      # 한쪽에만 있는 것
        "is_subset": sa <= sb,
    }


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert find_numbers([6, 3, 2, 10, -10], [10, 9, -5, 2, 3, 4, 5, -10]) == \
        [1, 0, 0, 1, 1, 0, 0, 1]
    assert count_numbers([6, 3, 2, 10, 10, 10, -10, -10, 7, 3],
                         [10, 9, -5, 2, 3, 4, 5, -10]) == [3, 0, 0, 1, 2, 0, 0, 2]
    assert intersection_sorted(["ohhenrie", "charlie", "baesangwook"],
                               ["baesangwook", "ohhenrie", "clarkson"]) == \
        ["baesangwook", "ohhenrie"]

    m = TwoWayMap(["tori", "sandage", "pikachu"])
    assert m.lookup("2") == "sandage"
    assert m.lookup("pikachu") == 3

    assert not_finished(["leo", "kiki", "eden"], ["eden", "kiki"]) == "leo"
    assert not_finished(["mislav", "stanko", "mislav", "ana"],
                        ["stanko", "ana", "mislav"]) == "mislav"

    assert most_common_value([1, 3, 2, 4, 3, 2]) == 2   # 2와 3 동률 -> 작은 값
    assert has_duplicate([1, 2, 2]) and not has_duplicate([1, 2, 3])
    assert group_by_length(["a", "bb", "cc", "ddd"]) == {1: ["a"], 2: ["bb", "cc"], 3: ["ddd"]}
    assert anagram_groups(["eat", "tea", "tan", "ate", "nat", "bat"]) == \
        [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]

    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([1, 2], 100) is None

    assert first_unique_char("leetcode") == 0
    assert first_unique_char("aabb") == -1

    assert longest_no_repeat("abcabcbb") == 3
    assert longest_no_repeat("bbbbb") == 1
    assert longest_no_repeat("pwwkew") == 3
    assert longest_no_repeat("") == 0

    assert clothes_combination([["yellow_hat", "headgear"],
                                ["blue_sunglasses", "eyewear"],
                                ["green_turban", "headgear"]]) == 5
    assert clothes_combination([["crow_mask", "face"],
                                ["blue_sunglasses", "face"],
                                ["smoky_makeup", "face"]]) == 3

    ops = set_ops([1, 2, 3], [3, 4])
    assert ops["union"] == [1, 2, 3, 4]
    assert ops["intersection"] == [3]
    assert ops["difference"] == [1, 2]
    assert ops["symmetric"] == [1, 2, 4]
    assert ops["is_subset"] is False

    print("03_hash.py  OK")
