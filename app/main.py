import time
import os
import json

EPSILON = 1e-9
REPEAT = 10


# ── MAC 연산 ──────────────────────────────────────────────
def mac(pattern, filter_):
    score = 0.0
    n = len(pattern)

    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_[i][j]
    return score


# ── 판정 ──────────────────────────────────────────────────
def judge(score_cross, score_x):
    if abs(score_cross - score_x) < EPSILON:
        return 'UNDECIDED'  
    return 'A' if score_cross > score_x else 'B'


# ── 성능 측정 ──────────────────────────────────────────────
def measure_time(pattern, filter_, repeat=REPEAT):
    total = 0.0
    for _ in range(repeat):
        start = time.perf_counter()     
        mac(pattern, filter_)
        end = time.perf_counter()
        total += (end - start) * 1000  # s -> ms 
    return total / repeat


# ── 입력 처리 ──────────────────────────────────────────────
def input_matrix(name, size=3):
    matrix = []
    print(f'{name} ({size}줄 입력, 공백 구분)')
    while len(matrix) < size:
        raw = input()
        try:
            row = list(map(float, raw.split()))
            if len(row) != size:
                raise ValueError
            matrix.append(row)
        except ValueError:
            print(f'입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.')
    return matrix


# ── 모드 1: 사용자 입력(3×3) ─────────────────────────────────
def run_mode1():
    print_div(1, '필터 입력')
    filter_a = input_matrix('필터 A')   # Cross
    filter_b = input_matrix('필터 B')   # X

    print_div(2, '패턴 입력')
    pattern = input_matrix('패턴')

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    result = judge(score_a, score_b)
    avg_ms = measure_time(pattern, filter_a)

    print_div(3, 'MAC 결과')
    print(f'A 점수: {score_a}\nB 점수: {score_b}')
    print(f'연산 시간(평균/{REPEAT}회): {avg_ms:.3f} ms')
    if result == 'UNDECIDED':
        print(f'판정: 판정 불가 (|A-B| < {EPSILON})')
    else:
        print(f'판정: {result}')

    return

# ── 모드 2: data.json 분석 ─────────────────────────────────
def run_mode2():
    pass

# ── Main ─────────────────────────────────────────────────
def main():
    print('=== Mini NPU Simulator ===\n')
    print('[모드 선택]')
    print('1. 사용자 입력 (3×3)')
    print('2. data.json 분석')
    mode = input('선택: ').strip()
    
    if mode == '1':
        run_mode1()
    elif mode == '2':
        run_mode2()
    else:
        print('잘못된 선택입니다. 1 또는 2를 입력하세요.')


if __name__ == '__main__':
    main()