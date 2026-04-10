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

    return


if __name__ == '__main__':
    main()