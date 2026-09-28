"""Create the 0.1.13 battle UI translation drafts without modifying game data."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from index_interface import source_text

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "work/translation/en/interface.index.json"
CATEGORY_PATH = ROOT / "work/translation/en/interface.executable_categories.json"
OUT = ROOT / "work/translation/en/battle_0.1.13"

NAMES = {
    "カイル": "Kyle", "ソノラ": "Sonora", "スカーレル": "Scarrel", "ヤード": "Yard",
    "アズリア": "Azria", "ギャレオ": "Gareo", "イスラ": "Isla", "ジャキーニ": "Jakiini",
    "クノン": "Kunnon", "フレイズ": "Fraise", "オルドレイク": "Ordraik", "ビジュ": "Biju",
    "オウキーニ": "Oukini", "ジルコーダ": "Zirkoda", "マルルゥ": "Marurur", "ヘイゼル": "Hazel",
    "ツェリーヌ": "Tselline", "ウィゼル": "Wizel", "アール": "Ahl", "オニビ": "Onibi",
    "キユピー": "Kyupy", "テコ": "Teco", "ディエルゴ": "Dielgo", "ロレイラル": "Loreilal",
    "シルターン": "Silturn", "サプレス": "Sapureth", "メイトルパ": "Maetropa",
}

EXACT = {
    "ユニットを移動させます": "Move the unit.", "物理攻撃を行います": "Make a physical attack.",
    "召喚魔法を使用します": "Use summon magic.", "特殊能力を使用します": "Use a special ability.",
    "道具を使用します": "Use an item.", "武器交換を行います": "Change weapons.",
    "待機型を変更します": "Change the ready stance.", "自軍のターンを終了します": "End your turn.",
    "ユニットの一覧を表示します": "View the unit list.", "召喚獣の詳細、組み合わせ結果などの": "View summon details and combination results.",
    "確認を行います": "", "戦闘を中断します": "Suspend the battle.",
    "参戦するユニットを決定してください": "Choose units to deploy.", "自分自身を対象としています": "Targets the user.",
    "これ以上食べられません": "Cannot eat any more.", "このお酒は飲めません": "Cannot drink this alcohol.",
    "敵には使用できません": "Cannot use on enemies.", "戦闘を開始しますか？": "Start the battle?",
    "ターンを終了しますか？": "End the turn?", "撤退しますか？": "Retreat?", "は　い": "Yes", "いいえ": "No",
    "敵の全撃破": "Defeat all enemies.", "敵リーダーの撃破": "Defeat the enemy leader.",
    "敵８体撃破": "Defeat 8 enemies.", "敵リーダーの全撃破": "Defeat all enemy leaders.",
    "石化": "Petrify", "魅了": "Charm", "凶暴化": "Berserk", "毒": "Poison", "マヒ": "Paralysis", "チャージ": "Charge",
    "暗闇": "Blind", "召喚封じ": "Summon Seal", "眠り": "Sleep", "応援": "Cheer", "ため": "Charge", "骨折": "Fracture",
    "隠密": "Stealth", "覚醒": "Awaken", "重症": "Severe Injury", "汚染": "Contamination", "瀕死": "Critical",
    "ステータス異常回復": "Cure Status Ailments", "主人公カルマ": "Protagonist Karma", "全憑依無効": "Immune to All Possession",
    "石": "Pet", "魅": "Cha", "凶": "Ber", "マ": "Par", "暗": "Bli", "封": "Seal", "眠": "Slp",
    "応": "Che", "た": "Chg", "隠": "Stl", "覚": "Awk", "重": "Inj", "汚": "Con", "瀕": "Crt", "ス": "Cur", "主": "Kar", "全": "All",
    "ＭＰが足りません": "Not enough MP.", "使用できません": "Cannot use.", "マヒ状態では使用できません": "Cannot use while paralyzed.",
    "武器を装備していません": "No weapon equipped.", "専用武器を装備していません": "Required weapon is not equipped.",
    "召喚石を装備していません": "No Summonite Stone equipped.", "召喚封じ状態では使用できません": "Cannot use while Summon Sealed.",
    "暗闇状態では使用できません": "Cannot use while blinded.", "もう変身できません": "Cannot transform again.",
    "協力攻撃の条件を満たしていません": "Cooperative-attack requirements are not met.", "もう抜剣できません": "Cannot draw the blade again.",
    "召喚ランクが足りません": "Summon rank is too low.", "この召喚獣は戦闘不能状態です": "This summon is incapacitated.",
    "既に召喚されています": "Already summoned.", "これ以上召喚することはできません": "Cannot summon any more.",
    "この召喚獣は異常状態です": "This summon has a status ailment.", "この召喚獣は憑依状態です": "This summon is possessed.",
    "「ユニット召喚」の特殊能力が必要です": "The Unit Summon special ability is required.", "別ユニット専用の召喚魔法です": "This summon magic is for another unit.",
    "サモンアシストの条件を満たしていません": "Summon Assist requirements are not met.", "お気に入り専用です": "For Favorites only.",
    "別ユニット専用の召喚獣です": "This summon is for another unit.", "この戦闘は撤退できません": "Cannot retreat from this battle.",
    "戦闘準備": "Battle Preparation", "戦闘開始": "Start Battle", "ユニット一覧": "Unit List", "戦況": "Battle Status",
    "範囲表示": "Show Range", "状態": "Status", "向き確認": "Check Facing", "配置変更": "Reposition", "向き変更": "Change Facing",
    "暴走召喚の使用で召喚石が壊れた！": "The Summonite Stone broke from using Rampage Summon!", "サモンアシスト": "Summon Assist",
    "選択／解除": "Select / Clear", "決定": "Confirm", "３マスの範囲内に協力者がいません": "No ally is within 3 spaces.",
    "協力者を選択してください": "Select an ally.", "これ以上選択できません": "Cannot select any more.", "移動": "Move", "闘気": "Fighting Spirit",
    "抗魔の領域": "Anti-Magic Field", "」を": "”,", "開始しますか？": "start?", "А選択　В戦闘情報確認": "A: Select   B: Battle Info",
    "主人公の得意召喚属性と戦闘タイプが": "The protagonist’s preferred summon affinity and battle type are", "未設定です": "not set.",
    "主人公の戦闘タイプが": "The protagonist’s battle type is", "得意召喚属性を選んでください": "Choose a preferred summon affinity.",
    "機属性": "Machine", "鬼属性": "Yokai", "霊属性": "Spirit", "獣属性": "Beast", "戦闘タイプを選んでください": "Choose a battle type.",
    "戦士タイプ　": "Warrior Type", "召喚師タイプ": "Summoner Type", "以上でよろしいですか？": "Is this correct?",
    "得意召喚属性：【機属性】": "Preferred Affinity: [Machine]", "得意召喚属性：【鬼属性】": "Preferred Affinity: [Yokai]",
    "得意召喚属性：【霊属性】": "Preferred Affinity: [Spirit]", "得意召喚属性：【獣属性】": "Preferred Affinity: [Beast]",
    "戦闘タイプ　：【戦士　】": "Battle Type: [Warrior]", "戦闘タイプ　：【召喚師】": "Battle Type: [Summoner]",
    "戦闘タイプ：【戦士　】": "Battle Type: [Warrior]", "戦闘タイプ：【召喚師】": "Battle Type: [Summoner]",
    "勝利条件": "Victory Conditions", "敗北条件": "Defeat Conditions", "設定されていません": "Not set.",
}

def replace_names(text):
    for source, target in NAMES.items():
        text = text.replace(source, target)
    return text

def executable_target(source):
    if source in EXACT:
        return EXACT[source]
    if source.startswith("Н"):
        body = replace_names(source[1:])
        phrases = {"海賊たち": "Pirates", "はぐれ召喚獣": "Stray Summons", "の防衛機械": " Defense Machines", "の鬼・妖怪": " Yokai", "の幽霊たち": " Ghosts", "の獣人たち": " Beastfolk", "率いる帝国軍部隊": "’s Imperial Unit", "海賊": "Pirate", "一味": " Crew", "帝国軍": "Imperial Army", "召喚蟲": "Summon Insect ", "女王蟲": "Queen Insect", "亡霊召喚師": "Ghost Summoner", "無色の派閥": "Colorless Faction", "亡霊たち": "Ghosts", "のディエルゴ": "’s Dielgo", "悪行召喚獣": "Evil Summon", "海賊の亡霊": "Pirate Ghost", "島の住人": "Island Residents", "謎の影": "Mysterious Shadow", "源罪の影": "Original Sin Shadow", "悪行魔獣": "Evil Beast", "悪行霊": "Evil Spirit", "狂った機械": "Mad Machine", "悪行妖怪": "Evil Yokai", "無色の亡霊": "Colorless Ghost", "幻影の戦士たち": "Phantom Warriors", "の機械兵士": " Machine Soldiers", "の幽霊": " Ghost", "の召喚獣": " Summons", "の魔天兵": " Demon Soldiers", "の悪業鬼": "Evil Oni", "の聖霊": "Holy Spirit", "の魔獣": "Magic Beast"}
        for a, b in phrases.items(): body = body.replace(a, b)
        return "Н" + body
    if source.startswith("主人公") and source.endswith("の戦闘不能"):
        return replace_names(source).replace("主人公", "Protagonist").replace("の戦闘不能", " Incapacitated")
    if source == "自軍の全戦闘不能": return "All allies incapacitated."
    victory = {"？？？？兵士の撃破": "Defeat the ???? Soldier.", "？？？本体の撃破": "Defeat the ??? Core.", "？？？？？を倒せ": "Defeat ?????!", "ディエルゴを倒せ！": "Defeat Dielgo!"}
    if source in victory: return victory[source]
    raise ValueError(source)

def table_target(category, source, offset):
    if category == "status_labels":
        extra = {"正常": "Normal", "召喚魔法が使用できなくなる": "Cannot use summon magic.", "行動するまで攻撃を受けない（移動時は効果持続）": "Cannot be attacked until acting (persists while moving).", "効果中はＺＯＣ効果が無効になる": "ZOC is disabled while active.", "抜剣": "Draw Blade", "全異常・憑依無効　暴走召喚使用可": "Immune to ailments and Possession; Rampage Summon enabled.", "復活": "Revive", "全異常無効": "Immune to all ailments", "骨折": "Fracture", "凶血の呪い": "Curse of Violent Blood", "ステータス異常回": "Cure Ailments", "材質破壊": "Material Break"}
        return extra.get(source, EXACT.get(source))
    if category == "attack_commands":
        attack = {"縦斬り":"Vertical Slash", "横斬り":"Horizontal Slash", "突き":"Thrust", "打撃":"Strike", "縦投げ":"Vertical Throw", "横投げ":"Horizontal Throw", "射る":"Shoot", "射撃":"Fire"}
        ranges = {"射程：隣接マス　上２　下２":"Range: Adjacent   Up 2   Down 2", "射程：隣接マス　上１　下２":"Range: Adjacent   Up 1   Down 2", "射程：隣接マス　上２　下３":"Range: Adjacent   Up 2   Down 3", "射程：隣接マス　上３　下２":"Range: Adjacent   Up 3   Down 2", "　　　斜めマス　上０　下１":"       Diagonal   Up 0   Down 1", "射程：隣接マス　上４　下３":"Range: Adjacent   Up 4   Down 3", "　　　２マス目　上３　下２":"       Second space   Up 3   Down 2", "射程：１～３　上下は距離により変動":"Range: 1–3   Height varies by distance", "障害物による攻撃不可あり":"Obstacles may block attacks", "射程：２～５　上下は距離により変動":"Range: 2–5   Height varies by distance", "射程：１～５　上下は距離により変動":"Range: 1–5   Height varies by distance", "障害物による攻撃不可あり　":"Obstacles may block attacks  "}
        return attack.get(source, ranges.get(source))
    if category == "help_and_menu_titles":
        return {"タイトル":"Title", "移動":"Move", "向きと高さ":"Facing and Height", "攻撃範囲と武器":"Attack Range and Weapons", "待機型":"Ready Stance", "状態異常":"Status Ailments", "障害物":"Obstacles", "スキル":"Skills", "召喚魔法":"Summon Magic", "召喚作成":"Create Summons", "属耐性":"Affinity Resistance", "サモンアシスト":"Summon Assist", "お気に入り召喚獣":"Favorite Summons", "抜剣覚醒":"Blade Awakening", "ブレイブバトル":"Brave Battle", "パーティ能力":"Party Abilities", "イベントバトル再戦":"Replay Event Battle", "料理":"Cooking", "ユニット召喚獣育成":"Raise Unit Summons", "レベルドレイン":"Level Drain", "傀儡招来":"Puppet Summon", "カルマ値":"Karma"}.get(source)
    return None

def objective_target(source):
    s = replace_names(source)
    exact = {
        "回復系アイテムの使用個数が３個以下":"Use 3 or fewer recovery items.", "戦闘中に使用した回復系アイテムの個数が３個以下":"Use 3 or fewer recovery items during battle.", "サポートユニットによる使用や料理アイテムは対象外":"Support-unit uses and cooking items do not count.", "ファーストアタックを決める":"Land the first attack.", "自軍と敵軍含めて、自軍ユニットが一番最初に攻撃を当てる":"Your unit must be the first to land an attack, among both sides.", "サモンアシストで敵を１体以上撃破する":"Defeat 1 or more enemies with Summon Assist.", "攻撃者よりも低レベルの敵を倒さない":"Do not defeat enemies below the attacker’s level.", "攻撃者よりも低レベルの敵を倒さない　同レベルはＯＫ":"Do not defeat enemies below the attacker’s level; equal level is allowed.", "ＳＰＯＴ参戦とアシスト参加者のレベルは対象外　":"Spot-deployed and assist participants’ levels do not count.", "一人も戦闘不能者を出さない":"Do not let anyone become incapacitated.", "一切戦闘不能者を出さない　自動抜剣覚醒は戦闘不能扱い":"Do not let anyone become incapacitated; automatic Blade Awakening counts as incapacitation.", "任意抜剣覚醒と、空蝉・サポートの戦闘不能回避は対象外":"Voluntary Blade Awakening and Utsusemi/support incapacitation avoidance do not count.",
    }
    if s in exact: return exact[s]
    patterns = [
        (r"(.+)が（?([０-９]+)）?体以上敵を撃破する", lambda m: f"{m.group(1)} defeats {m.group(2) or ''}+ enemies."),
        (r"(.+)を撃破する", lambda m: f"Defeat {m.group(1)}."),
        (r"([０-９]+)ターン以内にクリアする", lambda m: f"Clear within {m.group(1)} turns."),
        (r"障害物の爆発で敵を１体以上撃破する", lambda m: "Defeat 1+ enemies with an obstacle explosion."),
        (r"障害物で敵を１体以上毒にする", lambda m: "Poison 1+ enemies with an obstacle."),
        (r"障害物で敵を１体以上石化にする", lambda m: "Petrify 1+ enemies with an obstacle."),
    ]
    for pattern, make in patterns:
        match = re.fullmatch(pattern, s)
        if match: return make(match)
    return None

def row_entry(row, target, source_kind, table=None):
    entry = {"id": row["id"], "target_full": target, "source_sha256": row["source_sha256"], "source_offset": row["source_offset"], "source_control_tokens": row["source_control_tokens"], "source_kind": source_kind, "meaning_status": "draft_pending_meaning_review", "insertion_status": "not_inserted_or_layout_validated"}
    if source_kind == "executable": entry["module_address"] = row["module_address"]
    else: entry["references"] = row["references"]; entry["table_id"] = table["id"]; entry["table_source_sha256"] = table["source_sha256"]
    return entry

def collect():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8")); categories = json.loads(CATEGORY_PATH.read_text(encoding="utf-8"))
    by_ordinal = {}
    for group in categories["groups"]:
        for ordinal in range(group["first_ordinal"], group["last_ordinal"] + 1): by_ordinal[ordinal] = group["category"]
    executable_groups = {"battle_command_help", "battle_item_restrictions", "battle_confirmation_dialog", "battle_encounter_titles", "battle_victory_conditions", "battle_defeat_conditions", "status_effect_names", "status_effect_abbreviations", "battle_action_restrictions", "battle_menu_commands", "summon_assist_battle_help", "battle_field_effect_labels", "battle_replay_start_dialog", "protagonist_affinity_battle_type_setup", "battle_condition_labels"}
    exe, tab, skipped = [], [], []
    for ordinal,row in enumerate(index["executable_literals"]):
        if by_ordinal.get(ordinal) not in executable_groups: continue
        source = source_text(row["id"], index)
        try: target = executable_target(source)
        except ValueError: skipped.append({"id":row["id"],"reason":"no executable translation rule"}); continue
        exe.append(row_entry(row,target,"executable"))
    wanted_tables = {"status_labels", "attack_commands", "help_and_menu_titles", "common_brave_conditions", "battle_brave_conditions"}
    for table in index["tables"]:
        if table["category"] not in wanted_tables: continue
        for row in table["strings"]:
            if not row["contains_japanese"]: continue
            source = source_text(row["id"], index)
            in_scope = (table["category"] != "attack_commands" or row["source_offset"] < 0x553a) and (table["category"] != "help_and_menu_titles" or row["source_offset"] <= 0x15d2)
            if not in_scope: continue
            target = objective_target(source) if table["category"] in {"common_brave_conditions","battle_brave_conditions"} else table_target(table["category"],source,row["source_offset"])
            if target is None: skipped.append({"id":row["id"],"reason":"outside bounded battle UI scope or no table translation rule"}); continue
            tab.append(row_entry(row,target,"table",table))
    return index, exe, tab, skipped

def document(entries, scope, exclusions):
    return {"schema_version":1,"language":"en","status":"draft_pending_meaning_review","build_version":"0.1.13","scope":scope,"source_index_path":"work/translation/en/interface.index.json","source_index_sha256":hashlib.sha256(INDEX_PATH.read_bytes()).hexdigest(),"excluded_rows":exclusions,"entries":entries}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--write",action="store_true"); args=parser.parse_args()
    index, exe, tab, skipped=collect()
    report={"mode":"write" if args.write else "dry_run","executable_entries":len(exe),"table_entries":len(tab),"skipped_count":len(skipped),"skipped_sample":skipped[:12]}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not args.write: return
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/"executable.targets.json").write_text(json.dumps(document(exe,"Battle deployment, commands, status, encounter labels, confirmations, victory/defeat and battle setup.",[]),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"table.targets.json").write_text(json.dumps(document(tab,"Battle status, base attack modes/ranges, tutorial navigation, and directly translated Brave Battle objectives. Named skills/items and unresolved named/multiline conditions are deliberately excluded.",skipped),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
