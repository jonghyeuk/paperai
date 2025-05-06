import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator

# 논문 DB 파일 경로 (앱과 동일한 폴더 또는 업로드 위치에 있어야 함)
DB_PATH = "ISEF Final DB.xlsx"

# 논문 DB에서 유사한 주제 찾기
def search_similar_papers(keyword):
    try:
        df = pd.read_excel(DB_PATH)
        df = df.dropna(subset=["Project Title"])
        titles = df["Project Title"].astype(str).tolist()

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(titles)
        user_vec = vectorizer.transform([keyword])
        similarities = cosine_similarity(user_vec, tfidf_matrix).flatten()

        top_indices = similarities.argsort()[::-1][:3]  # 유사도 상위 3개
        results = []
        for idx in top_indices:
            row = df.iloc[idx]
            translated_title = GoogleTranslator(source='en', target='ko').translate(row['Project Title'])
            abstract = row.get("Abstract", "")
            translated_abstract = GoogleTranslator(source='en', target='ko').translate(abstract[:500]) if abstract else "요약 없음"

            results.append({
                "title_en": row['Project Title'],
                "title_ko": translated_title,
                "abstract_ko": translated_abstract,
                "year": row.get("Year", "연도 없음"),
                "award": row.get("Awards Won", "")
            })
        return results

    except Exception as e:
        print("[Error in DB search]", e)
        return []
