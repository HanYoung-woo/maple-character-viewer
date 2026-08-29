import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="서버별 메이플 캐릭터 통합 조회기", 
    page_icon="🍁", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 [CSS 스타일 설정]
st.markdown("""
<style>
.char-card {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: flex-start;
    background-color: #0e1117;
    border: 1px solid rgba(250, 250, 250, 0.2);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    width: 100%;
    gap: 20px;
    box-sizing: border-box;
}
.img-box {
    flex: 0 1 180px;
    min-width: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.char-image {
    width: 100% !important;
    height: auto !important;
    max-width: 180px;
    object-fit: contain;
    display: block;
    transform: scale(1.4);
    transform-origin: center center;
    margin-top: -15px !important;
    margin-bottom: -15px !important;
    margin-left: auto;
    margin-right: auto;
}
.info-box {
    flex: 1 1 auto;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.info-row {
    font-size: 14px;
    line-height: 1.4;
    word-break: break-word;
}
.account-badge {
    background-color: #1e3799;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 4px;
}

/* 🔗 링크스킬 3행 4열 그리드 레이아웃 */
.link-section {
    margin-top: 4px;
}
.link-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-top: 4px;
    margin-bottom: 10px;
}
.link-item {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(250, 250, 250, 0.1);
    border-radius: 4px;
    padding: 4px 6px;
    min-width: 0;
}
.link-item img {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}
.link-text {
    font-size: 11px;
    color: #ddd;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

# 💡 [계정 및 캐릭터 관리] 
MY_ACCOUNTS = {
    "메인 계정": [
        {"name": "푼수Len", "server": "노바", "level": 275, "job": "패스파인더"},
        {"name": "푼수윈브s", "server": "스카니아", "level": 260, "job": "나이트로드"},
        {"name": "푼수제로", "server": "스카니아", "level": 260, "job": "나이트로드"},
        {"name": "본캐릭터3", "server": "루나", "level": 250, "job": "아델"}
    ],
    "부계정 1": [
        {"name": "부캐릭터A", "server": "이노시스", "level": 250, "job": "아델"},
        {"name": "부캐릭터B", "server": "스카니아", "level": 230, "job": "비숍"}
    ],
    "부계정 2": [
        {"name": "부캐릭터C", "server": "오로라", "level": 220, "job": "섀도어"}
    ]
}

SERVER_ORDER = ["스카니아", "루나", "베라", "크로아", "유니온", "엘리시움", "제니스", "노바", "이노시스", "오로라", "리부트", "리부트2"]

# 💡 Secrets에 설정된 API Key를 가져오고, 없으면 사이드바 입력창을 보여주는 안전한 방식
if "NEXON_API_KEY" in st.secrets:
    API_KEY = st.secrets["NEXON_API_KEY"]
else:
    with st.sidebar:
        st.header("⚙️ 설정")
        API_KEY = st.text_input("API 키 입력", type="password")
        
        st.markdown("---")
        st.subheader("📂 메이플 계정 선택")
        selected_account = st.selectbox("조회할 계정을 선택하세요", list(MY_ACCOUNTS.keys()))
        available_characters = MY_ACCOUNTS[selected_account]
        
        st.markdown("---")
        st.subheader(f"📌 {selected_account} 캐릭터 선택")
        
        characters_by_server = {}
        for char_info in available_characters:
            srv = char_info["server"]
            if srv not in characters_by_server:
                characters_by_server[srv] = []
            characters_by_server[srv].append(char_info)
        
        sorted_servers_for_sidebar = sorted(
            characters_by_server.keys(), 
            key=lambda x: SERVER_ORDER.index(x) if x in SERVER_ORDER else 999
        )
        
        selected_chars = []
        for server_name in sorted_servers_for_sidebar:
            chars = characters_by_server[server_name]
            with st.expander(f"🏰 {server_name} 서버", expanded=True):
                for char_info in chars:
                    c_name = char_info["name"]
                    c_level = char_info["level"]
                    c_job = char_info["job"]
                    label = f"{c_name} (Lv.{c_level} / {c_job})"
                    if st.checkbox(label, value=True, key=f"chk_{selected_account}_{server_name}_{c_name}"):
                        selected_chars.append(c_name)
            
        st.markdown("---")
        load_btn = st.button("🔄 캐릭터 정보 조회", use_container_width=True)

st.title("🍁 서버별 메이플스토리 캐릭터 통합 조회기")

if load_btn:
    if not API_KEY:
        st.warning("⚠️ API 키를 입력해주세요!")
    elif not selected_chars:
        st.warning("⚠️ 조회할 캐릭터를 하나 이상 체크해주세요!")
    else:
        headers = {
            "accept": "application/json",
            "x-nxopen-api-key": API_KEY.strip()
        }
        
        # 기본 조회 기준: 어제 날짜
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        # 새벽 집계중 에러(OPENAPI00009) 대비 2일 전 날짜 준비
        two_days_ago_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        st.info(f"[{selected_account}] 데이터 수집 중입니다... (기준일자: {yesterday_date})")
        
        servers_data = {}
        failed_chars = []

        for name in selected_chars:
            ocid_url = f"https://open.api.nexon.com/maplestory/v1/id?character_name={name}"
            res = requests.get(ocid_url, headers=headers)
            
            if res.status_code == 200:
                ocid = res.json().get("ocid")
                
                # 💡 어제 날짜로 우선 시도하고, OPENAPI00009 에러 발생 시 그저께 날짜로 자동 전환
                target_date = yesterday_date
                basic_url = f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}&date={target_date}"
                b_res = requests.get(basic_url, headers=headers)
                
                # 데이터가 준비 안 된 경우(새벽 시간 등) 2일 전 데이터로 재시도
                if b_res.status_code != 200 and "OPENAPI00009" in b_res.text:
                    target_date = two_days_ago_date
                    basic_url = f"https://open.api.nexon.com/maplestory/v1/character/basic?ocid={ocid}&date={target_date}"
                    b_res = requests.get(basic_url, headers=headers)

                # 다른 엔드포인트도 결정된 target_date로 호출
                pop_url = f"https://open.api.nexon.com/maplestory/v1/character/popularity?ocid={ocid}&date={target_date}"
                p_res = requests.get(pop_url, headers=headers)

                item_url = f"https://open.api.nexon.com/maplestory/v1/character/item-equipment?ocid={ocid}&date={target_date}"
                i_res = requests.get(item_url, headers=headers)
                
                ability_url = f"https://open.api.nexon.com/maplestory/v1/character/ability?ocid={ocid}&date={target_date}"
                a_res = requests.get(ability_url, headers=headers)
                
                link_url = f"https://open.api.nexon.com/maplestory/v1/character/link-skill?ocid={ocid}&date={target_date}"
                l_res = requests.get(link_url, headers=headers)

                if b_res.status_code == 200:
                    b_data = b_res.json()
                    
                    popularity = 0
                    if p_res.status_code == 200:
                        p_data = p_res.json()
                        popularity = p_data.get("popularity", 0) or 0

                    world_name = b_data.get("world_name", "기타 서버")
                    cur_exp = b_data.get("character_exp", 0)
                    exp_rate = b_data.get("character_exp_rate", "0.00")

                    liberation_status = "미완료"
                    if i_res.status_code == 200:
                        items = i_res.json().get("item_equipment", [])
                        for item in items:
                            item_name = item.get("item_name", "")
                            if "제네시스" in item_name:
                                liberation_status = "제네시스 무기 해방"
                                break
                            elif "데스티니" in item_name:
                                liberation_status = "데스티니 무기 해방"
                                break

                    guild_name = b_data.get("character_guild_name")
                    guild_level = "정보 없음"
                    guild_gp = 0
                    guild_alliance_name = "연합 없음"
                    attendance_status = "미출석"
                    
                    if guild_name:
                        try:
                            guild_id_url = f"https://open.api.nexon.com/maplestory/v1/guild/id?guild_name={guild_name}&world_name={world_name}"
                            g_id_res = requests.get(guild_id_url, headers=headers)
                            if g_id_res.status_code == 200:
                                oguild_id = g_id_res.json().get("oguild_id")
                                
                                guild_basic_url = f"https://open.api.nexon.com/maplestory/v1/guild/basic?oguild_id={oguild_id}&date={target_date}"
                                g_basic_res = requests.get(guild_basic_url, headers=headers)
                                if g_basic_res.status_code == 200:
                                    g_data = g_basic_res.json()
                                    guild_level = g_data.get("guild_level", "-")
                                    guild_gp = g_data.get("guild_point", 0)
                                    guild_alliance_name = g_data.get("guild_alliance_name") or "연합 없음"

                                guild_member_url = f"https://open.api.nexon.com/maplestory/v1/guild/member?oguild_id={oguild_id}&date={target_date}"
                                g_mem_res = requests.get(guild_member_url, headers=headers)
                                if g_mem_res.status_code == 200:
                                    members = g_mem_res.json().get("guild_member", [])
                                    for m in members:
                                        if m.get("character_name") == name:
                                            member_gp = m.get("character_gp", 0)
                                            if member_gp > 0:
                                                attendance_status = f"출석 (기여도: {member_gp:,} GP)"
                                            else:
                                                attendance_status = "미출석"
                                            break
                        except Exception:
                            pass
                    else:
                        guild_name = "길드 없음"

                    ability_info = {"1": "정보 없음", "2": "정보 없음", "3": "정보 없음"}
                    ability_point = 0
                    if a_res.status_code == 200:
                        a_data = a_res.json()
                        ability_point = a_data.get("remain_fame", 0)
                        presets = ["ability_preset_1", "ability_preset_2", "ability_preset_3"]
                        for idx, p_key in enumerate(presets, 1):
                            p_data = a_data.get(p_key)
                            if p_data and p_data.get("ability_info"):
                                lines = [f"[{item.get('ability_grade')}] {item.get('ability_value')}" for item in p_data.get("ability_info")]
                                ability_info[str(idx)] = " / ".join(lines)

                    link_presets = {"1": [], "2": [], "3": []}
                    if l_res.status_code == 200:
                        l_data = l_res.json()
                        preset_keys = [
                            ("1", "character_link_skill_preset_1"),
                            ("2", "character_link_skill_preset_2"),
                            ("3", "character_link_skill_preset_3")
                        ]
                        for p_num, p_key in preset_keys:
                            skills = l_data.get(p_key, [])
                            for s in skills:
                                link_presets[p_num].append({
                                    "name": s.get("skill_name"),
                                    "level": s.get("skill_level"),
                                    "icon": s.get("skill_icon")
                                })

                    char_info = {
                        "name": name,
                        "account": selected_account,
                        "level": b_data.get("character_level"),
                        "job": b_data.get("character_class"),
                        "gender": b_data.get("character_gender"),
                        "image": b_data.get("character_image"),
                        "date_create": b_data.get("character_date_create", "")[:10] if b_data.get("character_date_create") else "-",
                        "cur_exp": cur_exp,
                        "exp_rate": exp_rate,
                        "popularity": popularity,
                        "liberation": liberation_status,
                        "guild_name": guild_name,
                        "guild_level": guild_level,
                        "guild_gp": guild_gp,
                        "guild_alliance": guild_alliance_name,
                        "attendance": attendance_status,
                        "ability_info": ability_info,
                        "ability_point": ability_point,
                        "link_presets": link_presets
                    }
                    
                    if world_name not in servers_data:
                        servers_data[world_name] = []
                    servers_data[world_name].append(char_info)
                else:
                    failed_chars.append(f"{name} (기본정보 실패: Status {b_res.status_code} - {b_res.text})")
            else:
                failed_chars.append(f"{name} (OCID 조회 실패: Status {res.status_code} - {res.text})")
        
        # 화면 출력
        if not servers_data:
            st.error("❌ 캐릭터 정보를 불러오지 못했습니다. 아래 상세 원인을 확인해주세요.")
            if failed_chars:
                for err in failed_chars:
                    st.error(f"• {err}")
        else:
            if failed_chars:
                with st.expander("⚠️ 일부 캐릭터 조회 실패 내역", expanded=False):
                    for err in failed_chars:
                        st.write(f"• {err}")
                
            sorted_server_names = sorted(
                servers_data.keys(),
                key=lambda x: SERVER_ORDER.index(x) if x in SERVER_ORDER else 999
            )
            
            tabs = st.tabs([f"🏰 {server}" for server in sorted_server_names])
            
            for i, server in enumerate(sorted_server_names):
                with tabs[i]:
                    st.subheader(f"[{server}] 서버 캐릭터 리스트")
                    
                    for char in servers_data[server]:
                        exp_str = f"{char['cur_exp']:,} EXP ({char['exp_rate']}%)"
                        guild_display = f"{char['guild_name']} (Lv.{char['guild_level']} | GP: {char['guild_gp']:,})" if isinstance(char['guild_gp'], int) else f"{char['guild_name']}"
                        
                        img_html = f'<img src="{char["image"]}" class="char-image" />' if char['image'] else ''
                        ab1 = char['ability_info']['1']
                        ab2 = char['ability_info']['2']
                        ab3 = char['ability_info']['3']

                        link_html_blocks = []
                        for p_idx in ["1", "2", "3"]:
                            skills = char["link_presets"][p_idx]
                            items_html = ""
                            if skills:
                                for s in skills:
                                    icon_tag = f'<img src="{s["icon"]}" />' if s.get("icon") else ''
                                    items_html += (
                                        f'<div class="link-item">'
                                        f'{icon_tag}'
                                        f'<span class="link-text"><b>Lv.{s["level"]}</b> {s["name"]}</span>'
                                        f'</div>'
                                    )
                            else:
                                items_html = '<div style="font-size: 11px; color: #777; grid-column: span 4;">장착된 스킬 없음</div>'
                            
                            link_html_blocks.append(
                                f'<div class="link-section-title" style="font-size: 11px; color: #aaa; margin-top: 4px;"><b>[프리셋 {p_idx}]</b></div>'
                                f'<div class="link-grid">{items_html}</div>'
                            )
                        
                        full_link_html = "".join(link_html_blocks)

                        raw_html = (
                            f'<div class="char-card">'
                            f'<div class="img-box">'
                            f'{img_html}'
                            f'<span style="font-size: 12px; color: #aaa; margin-top: 6px;">인기도: {char["popularity"]:,}</span>'
                            f'</div>'
                            f'<div class="info-box">'
                            f'<div><span class="account-badge">{char["account"]}</span>'
                            f'<h3 style="margin: 0; padding: 0; display: inline-block; margin-left: 6px;">{char["name"]} <span style="font-size: 16px; font-weight: normal; color: #ddd;">(Lv.{char["level"]})</span></h3></div>'
                            f'<div class="info-row"><b>직업:</b> {char["job"]} | <b>성별:</b> {char["gender"]} | <b>생성일:</b> {char["date_create"]}</div>'
                            f'<div class="info-row"><b>경험치:</b> {exp_str}</div>'
                            f'<div class="info-row"><b>해방 여부:</b> <span style="color: #ff4b4b; font-weight: bold;">{char["liberation"]}</span></div>'
                            f'<div class="info-row">🛡️ <b>길드:</b> {guild_display} | 🔗 <b>연합:</b> {char["guild_alliance"]}</div>'
                            f'<div class="info-row">📌 <b>길드 출석:</b> <span style="color: #2ed573; font-weight: bold;">{char["attendance"]}</span></div>'
                            f'<hr style="border: 0; border-top: 1px solid rgba(250,250,250,0.1); margin: 6px 0;" />'
                            f'<div class="info-row"><b>💡 어빌리티 (보유 명성치: {char["ability_point"]:,})</b></div>'
                            f'<div style="font-size: 12px; color: #ccc; line-height: 1.4;">'
                            f'<div><b>[1번]</b> {ab1}</div>'
                            f'<div><b>[2번]</b> {ab2}</div>'
                            f'<div><b>[3번]</b> {ab3}</div>'
                            f'</div>'
                            f'<hr style="border: 0; border-top: 1px solid rgba(250,250,250,0.1); margin: 6px 0;" />'
                            f'<div class="info-row"><b>🔗 링크 스킬 정보</b></div>'
                            f'<div class="link-section">{full_link_html}</div>'
                            f'</div>'
                            f'</div>'
                        )
                        
                        st.markdown(raw_html, unsafe_allow_html=True)
else:
    st.info("👈 사이드바에서 계정을 고르고, 서버별 아코디언을 열어 캐릭터를 선택한 뒤 **[캐릭터 정보 조회]** 버튼을 눌러주세요!")