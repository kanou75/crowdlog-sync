from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from concurrent.futures import ThreadPoolExecutor
import requests

# router = APIRouter()
app = FastAPI()

@app.get("/sync")
def main():
    """
    Syncs data from CrowdLog to kintone
    """
    result = []
    page = 1
    while True:
        try:
            url = 'https://api.crowdlog.jp/projects?per_page=100&with=members&with=customer&with=business&with=department&active=true&page=' + str(page)
            # クラウドログのプロジェクトデータを全て取得(100件まで)
            crowdlogProjects = sendapi(
                url,
                {"Authorization": "Bearer mhrMaJHwUMRM5-NGLcFhKgRZ5rRyhkhPbWbGsxCy"}
            )

            # クラウドログのプロジェクトが存在する場合
            if(len(crowdlogProjects['projects']) > 0):

                # projectsの数だけループ
                for item in crowdlogProjects['projects']:
                    members = item["members"]

                    # === ダミー予算が既に存在するかチェック ===
                    has_dummy = any(
                        member.get("id") == 181555
                        for member in members
                    )
                    print(has_dummy, item['code'])

                    if has_dummy:
                        # 更新対象外
                        result.append({
                            "project_id": item["id"],
                            "status": "skip",
                            "reason": "ダミー予算が既に存在"
                        })
                        continue

                    # クラウドログのプロジェクトメンバーを更新する
                    url_put = 'https://api.crowdlog.jp/projects/' + str(item['id']) + '/members/181555'
                    crowdlogProjects = sendapi_put(
                        url_put,
                        {"Authorization": "Bearer mhrMaJHwUMRM5-NGLcFhKgRZ5rRyhkhPbWbGsxCy"}
                    )

                page = page + 1

            else:
                return {
                    "message": "更新に成功しました。",
                    "result": result
                }
                # break

        except Exception as e:
            content = {
                    "message": "更新中にエラーが発生しました。",
                    "result": result,
                    "error": str(e)
                }
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


def sendapi(url, headers):
    response = requests.get(url,headers=headers)
    return response.json()

def sendapi_put(url,headers):
    response = requests.put(url,headers=headers)
    response.raise_for_status()
    return response.json() if response.text else {}

# # === スクリプト実行 ===
# if __name__ == "__main__":
#     main()