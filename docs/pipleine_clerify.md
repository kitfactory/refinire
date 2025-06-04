# ClearifyPipelineについて

ClearifyPipelineは要件を明確化するのに必要なAgentPipelineのサブクラスです。次のステップへ要件が満たされているかを確認されるまで、繰り返し質問を行い、ユーザーに確認を行います。

```python
class ReportRequirements(BaseModel):
    event: str  # イベント名
    date: str   #　日付
    place: str  # 場所
    topics: List[str] # トピック
    interested: str # 印象に残ること
    expression: str # 感想

pipeline = ClearifyPipeline(
    name="clearify_report_requrements",
    generation_instructions="""
    あなたはレポートを作成する準備を行います。
    レポートに記載する要件を整理し、魅力的なレポートとなるよう聞き手として、ユーザーと対話し要件を引き出してください。
    要件が明確でなかったり、魅力的出ない場合は、さらに質問をくりかえしてください。
    必要な項目と、それを魅力的にするポイントを伝えたり、サンプルを提示して、ユーザーの体験からレポートを作成するための、出来るだけ詳細な材料を集めてください。
    """,
    output_data = ReportRequirements,
    clerify_max_turns = 20,
    evaluation_instructions=None,
    model="gpt-4o"
)
result = pipeline.run("I would like to make a xxxx")

```

ClearifyPipelineはユーザーからの要望された要件に加えて、pydantic basemodelで出力型が定義されている場合は、ユーザーの出力型をラップし、次のようなクラスとしてLLMに出力させるようにしてください。

```python
class Clearify[T](BaseModel):
    clearity: bool  # Trueなら要件が確定
    user_requirement: T # Option True時に発生
```

ユーザーから型が指定されていないは文字列として要件を取得し、要件を返却するようにしてください。

```python
class Clearify(BaseModel):
    clearity: bool  # Trueなら要件が確定
    user_requirement: str # Option True時に発生
```
