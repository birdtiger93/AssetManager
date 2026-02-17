# 📈 KIS AssetManager & Automated Trader

한국투자증권(KIS) OpenAPI를 활용한 통합 자산 관리 및 자동 매매 시스템입니다. 국내/해외 주식의 잔고 현황을 실시간으로 모니터링하고, 설정한 실시간 전략에 따라 자동으로 주문을 실행합니다.

## ✨ 주요 기능

*   **통합 대시보드**: 국내 및 해외(미국) 자산을 한눈에 확인 (KRW 합산 및 개별 통화 표시).
*   **실시간 모니터링**: 1분마다 KIS API로부터 실시간 가격 및 잔고 데이터를 동기화.
*   **자동 자산 기록**: 매시간 및 장 마감 시 자산 현황을 데이터베이스(SQLite)에 스냅샷으로 저장하여 수익률 추이 관리.
*   **주문 시스템**: 현대적인 웹 UI를 통한 국내/해외 주식 실시간 매수/매도 주문.
*   **알고리즘 트레이딩**: `strategy.py`를 통해 사용자 정의 매매 전략 구현 및 1분 단위 자동 실행.
*   **보안 토큰 관리**: KIS API 토큰(24시간 유효) 자동 갱신 및 파일 캐싱 시스템 탑재.

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLite & SQLAlchemy (ORM)
- **Task Scheduler**: APScheduler (Background Jobs)
- **API Communication**: Requests

### Frontend
- **Framework**: React + Vite
- **Styling**: Tailwind CSS v4
- **Charts**: Recharts (Visual Data Distribution)
- **Icons**: Lucide React

## 📂 프로젝트 구조

```text
AssetManager/
├── config/             # 설정 파일 (API 키, 계좌 정보)
├── data/               # SQLite 데이터베이스 파일 저장소
├── frontend/           # React 프론트엔드 프로젝트
├── src/                # 백엔드 핵심 소스 코드
│   ├── api/            # KIS API Wrapper (국내/해외)
│   ├── auth/           # 토큰 관리 및 인증 로직
│   ├── database/       # DB 엔진 및 테이블 모델 정의
│   ├── logic/          # 수익률 계산, 주문 실행 및 매매 전략
│   └── web/            # FastAPI 라우터 및 API 서버
├── start_local.bat     # Windows 통합 실행 스크립트
├── start_local.sh      # WSL/Linux 통합 실행 스크립트
└── docker-compose.yml  # Docker 오케스트레이션 (선택 사항)
```

## 🚀 시작하기

### 1. 사전 준비 (Prerequisites)
*   **Python 3.10+**: 백엔드 구동용.
*   **Node.js 18+**: 프론트엔드 빌드 및 구동용.
*   **KIS OpenAPI 계정**: 한국투자증권에서 앱 키(App Key)와 시크릿(Secret)을 발급받아야 합니다.

### 2. 설정 (Configuration)
`config/secrets.yaml` 파일을 생성하거나 수정하여 정보를 입력합니다.
```yaml
api:
  app_key: "YOUR_APP_KEY"
  app_secret: "YOUR_APP_SECRET"
  account_no: "12345678"  # 계좌번호 8자리
  account_code: "01"     # 계좌 상품코드 (보통 01)
```

### 3. 설치 (Installation)
```bash
# 백엔드 의존성 설치
pip install -r requirements.txt

# 프론트엔드 의존성 설치
cd frontend
npm install
cd ..
```

### 4. 실행 (Running)
가장 간편한 방법은 통합 스크립트를 사용하는 것입니다.

*   **Windows**: `start_local.bat` 더블 클릭.
*   **WSL/Linux**: `bash start_local.sh`

실행 후 아래 주소로 접속하세요:
*   **Dashboard**: [http://localhost:5173](http://localhost:5173)
*   **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🤖 자동 매매 전략 설정
현재 1분마다 `src/logic/strategy.py`의 `run_strategy()` 함수가 자동 호출됩니다. 본인만의 매매 로직을 해당 함수 안에 구현하면 즉시 자동 매매가 시작됩니다.

```python
# src/logic/strategy.py 예시
def run_strategy():
    # 1. 가격 조회
    # 2. 조건 확인 (예: RSI < 30)
    # 3. 주문 실행
    # executor.execute_order(AssetType.STOCK_DOMESTIC, "005930", "BUY", 10, 70000)
    pass
```

## 📝 라이선스
개별 프로젝트 목적에 따라 자유롭게 사용 및 수정이 가능합니다.
