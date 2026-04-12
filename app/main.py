import time
import os
import json
import re

EPSILON = 1e-9
REPEAT = 10
CROSS = 'Cross'
X = 'X'


# ── 라벨 정규화 ──────────────────────────────────────────────
def normalize_label(label):
    label = label.strip().lower()
    if label in ('+', 'cross'):
        return CROSS
    elif label == 'x':
        return X
    else:
        raise ValueError(f'알 수 없는 라벨: {label!r}')
    

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
    return CROSS if score_cross > score_x else X


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
    data_path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'오류: {data_path} 파일을 찾을 수 없습니다.')
        return
    except json.JSONDecodeError as e:
        print(f'오류: data.json 파싱 실패 — {e}')
        return

    print_div(1, '필터 로드')
    raw_filters = data.get('filters', {})
    filters = {}

    for size_key, filter in raw_filters.items():
        loaded = {}
        for label_key, matrix in filter.items():
            try:
                std_label = normalize_label(label_key)
                loaded[std_label] = matrix
            except ValueError as e:
                print(f'  경고: {size_key} 필터 라벨 정규화 실패 — {e}')

            filters[size_key] = loaded
            labels = ', '.join(loaded.keys())
            print(f'  ✓ {size_key} 필터 로드 완료 ({labels})')

    
    print_div(2, '패턴 분석 (라벨 정규화 적용)')
    patterns = data.get('patterns', {})
    failed_cases = []
    perf_data = {} 
    cnt = 0
    passed = 0

    for pattern_id, pattern in patterns.items():
        print(f'\n  --- {pattern_id} ---')
        cnt += 1

        # 키에서 크기(N) 추출
        match = re.match(r'size_(\d+)_\d+', pattern_id) # () -> group 추출, d(digit) -> 숫자
        if not match:
            reason = '키 형식 오류'
            print(f'  [FAIL] {reason}: {pattern_id}')
            failed_cases.append(pattern_id, reason)
            continue

        n = int(match.group(1))
        size_key = f'size_{n}'

        # 필터 존재 확인
        if size_key not in filters:
            reason = '필터 없음'
            print(f'  [FAIL] {reason}: {pattern_id}')
            failed_cases.append((pattern_id, reason))
            continue

        filter_cross = filters[size_key].get(CROSS)
        filter_x = filters[size_key].get(X)

        if filter_cross is None or filter_x is None:
            reason = f'{size_key}에 Cross or X 필터가 없음'
            print(f'  [FAIL] {reason}')
            failed_cases.append((pattern_id, reason))
            continue

        matrix = pattern.get('input')
        expected_raw = pattern.get('expected', '')

        # 크기 검증
        n_pat = len(matrix) if matrix else 0
        n_flt = len(filter_cross)
        if n_pat != n_flt:
            reason = f'크기 불일치 (패턴={n_pat}×{n_pat}, 필터={n_flt}×{n_flt})'
            print(f'  [FAIL] {reason}')
            failed_cases.append((pattern_id, reason))
            continue

        # expected 정규화
        try:
            expected = normalize_label(expected_raw)
        except ValueError:
            reason = f'expected 라벨 정규화 실패: {expected_raw!r}'
            print(f'  [FAIL] {reason}')
            failed_cases.append((pattern_id, reason))
            continue


        # MAC 연산
        score_cross = mac(matrix, filter_cross)
        score_x = mac(matrix, filter_x)
        result = judge(score_cross, score_x)

        # PASS / FAIL 판정
        print(f'  Cross 점수: {score_cross}')
        print(f'  X 점수: {score_x}')

        if result == 'UNDECIDED':
            verdict = 'FAIL'
            reason = f'동점(UNDECIDED) 처리 규칙에 따라 FAIL'
            print(f'  판정: UNDECIDED | expected: {expected} | {verdict}')
        elif result == expected:
            verdict = 'PASS'
            print(f'  판정: {result} | expected: {expected} | {verdict}')
        else:
            verdict = 'FAIL'
            reason = f'판정={result}, expected={expected}'

        if verdict == 'PASS':
            passed += 1
        else:
            failed_cases.append((pattern_id, reason))

        # 성능 측정용 데이터 저장 (크기별 첫 번째 케이스만)
        if n not in perf_data:
            perf_data[n] = (matrix, filter_cross)

    # 성능 분석
    cross_3x3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    pattern_3x3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    perf_data.setdefault(3, (pattern_3x3, cross_3x3))

    analysis_data = []
    for n in sorted(perf_data.keys()):
        pattern, filter = perf_data[n]
        analysis_data.append((n, pattern, filter))
    print_perf(analysis_data)

    print_div(4, '결과 요약')
    print(f'총 테스트: {cnt}개')
    print(f'통과: {passed}개')
    print(f'실패: {len(failed_cases)}개')
    if failed_cases:
        print('\n실패 케이스:')
        for case_id, reason in failed_cases:
            print(f'  - {case_id}: {reason}')
    

# ── 작업 구분 Head 출력 ─────────────────────────────────────
def print_div(index ,prompt):
    print()
    print('#' + '-' * 39)
    print(f'# [{index}] {prompt}')
    print('#' + '-' * 39)


# ── 성능 분석 표 출력 ─────────────────────────────────────────
def print_perf(analysis_data):
    print_div('성능 분석', f'(평균/{REPEAT}회)')

    print(f'{"크기":<10} {"평균 시간(ms)":>14} {"연산 횟수(N²)":>14}')
    print('-' * 40)
    for n, pattern, filter_ in analysis_data:
        avg_ms = measure_time(pattern, filter_)
        ops = n * n
        print(f'{n}×{n:<7} {avg_ms:>14.3f} {ops:>14}')


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