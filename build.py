#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import io

# Windows 終端機輸出 UTF-8 設定（避免 emoji 導致 cp950 錯誤）
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def safe_print(msg):
    """Windows 安全輸出，自動處理無法編碼的字元"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

# 自動檢查並安裝 markdown 解析套件
try:
    import markdown
except ImportError:
    print("偵測到缺少 'markdown' 套件，正自動安裝中...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
    except Exception as e:
        print(f"安裝 markdown 套件失敗。錯誤訊息: {e}")
        print("請手動在終端機執行: pip install markdown")
        sys.exit(1)

def parse_front_matter(content):
    """
    解析 Markdown 頂部的 YAML Front Matter
    格式範例:
    ---
    title: "我的標題"
    date: "2026-06-20"
    tags: ["標籤1", "標籤2"]
    ---
    """
    meta = {}
    body = content
    # 匹配頂部的 --- ... ---
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        front_section = match.group(1)
        body = match.group(2)
        
        # 逐行解析 YAML 鍵值對
        for line in front_section.split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            
            # 去除引號
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            
            # 解析陣列，例如 ["A", "B"]
            if val.startswith('[') and val.endswith(']'):
                items = val[1:-1].split(',')
                val = []
                for item in items:
                    item = item.strip()
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        item = item[1:-1]
                    val.append(item)
                    
            meta[key] = val
            
    return meta, body

# HTML 範本：首頁 index.html
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_name} | 個人教學網站</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

    <!-- 頂部導覽列 (毛玻璃效果) -->
    <nav class="navbar">
        <div class="navbar-container">
            <a href="#" class="navbar-brand">{site_name}</a>
            <ul class="navbar-links">
                <li><a href="#about">關於我</a></li>
                <li><a href="#projects">精選作品</a></li>
                <li><a href="#lessons">教學文章</a></li>
                <li><a href="#parenting">親職教養資源</a></li>
                <li><a href="#resources">學習資源</a></li>
                <li><a href="#feedback">學生回饋</a></li>
            </ul>
        </div>
    </nav>

    <div class="container">
        <!-- Hero 視覺區 -->
        <header class="hero-section">
            <div class="hero-badge">🍎 Apple Learning Coach 認證教練</div>
            <h1 class="hero-title">哈囉，我是 {name}</h1>
            <p class="hero-subtitle">{title}</p>
            <div class="hero-cta">
                <a href="#lessons" class="btn btn-primary">開始學習</a>
                <a href="#about" class="btn btn-link">認識老師 &rsaquo;</a>
            </div>
            
            <div class="hero-stats">
                <div class="stat-item">
                    <span class="stat-num">20+ 年</span>
                    <span class="stat-label">教育現場深耕</span>
                </div>
                <div class="stat-item-divider"></div>
                <div class="stat-item">
                    <span class="stat-num">110+ 篇</span>
                    <span class="stat-label">教學日誌紀錄</span>
                </div>
                <div class="stat-item-divider"></div>
                <div class="stat-item">
                    <span class="stat-num">3 大</span>
                    <span class="stat-label">主要教學主題</span>
                </div>
            </div>
        </header>

        <!-- 關於我 Section -->
        <section id="about" class="about-section">
            <h2 class="section-title">關於我</h2>
            <div class="list-container" style="padding: 30px;">
                {about_content}
                <div style="margin-top: 20px; font-size: 14px; color: var(--text-secondary);">
                    <span>📧 Email: <a href="mailto:{email}">{email}</a></span>
                    <span style="margin-left: 20px;">🌐 GitHub: <a href="{github}" target="_blank">點此前往</a></span>
                </div>
            </div>
        </section>

        <!-- 精選作品 Section -->
        <section id="projects">
            <h2 class="section-title">精選作品</h2>
            <div class="card-grid">
                {project_cards}
            </div>
        </section>

        <!-- 教學紀錄 Section -->
        <section id="lessons">
            <div class="lessons-header">
                <h2 class="section-title" style="margin-bottom:0">最新教學紀錄</h2>
                <span class="lesson-count-badge"><span id="lessonVisibleCount">0</span> 篇文章</span>
            </div>

            <!-- 分類篩選列 -->
            <div class="filter-bar" id="lessonFilterBar">
                <button class="filter-chip active" data-filter="all" onclick="filterLessons(this)">📚 全部</button>
                <button class="filter-chip" data-filter="說數學" onclick="filterLessons(this)">🔢 說數學</button>
                <button class="filter-chip" data-filter="生生用平板" onclick="filterLessons(this)">📱 生生用平板</button>
                <button class="filter-chip" data-filter="iPad教學" onclick="filterLessons(this)">🍎 iPad教學</button>
            </div>

            <div class="list-container">
                <div id="lessonList">
                    {lesson_list}
                </div>
            </div>
        </section>

        <!-- 親職教養資源 Section -->
        <section id="parenting">
            <h2 class="section-title">親職教養參考資源 (網路轉載)</h2>
            <div class="list-container">
                {parenting_list}
            </div>
        </section>

        <!-- 學習資源 Section -->
        <section id="resources">
            <h2 class="section-title">推薦學習資源</h2>
            <div class="list-container" style="padding: 30px;">
                {resources_content}
            </div>
        </section>

        <!-- 學生回饋 Section -->
        <section id="feedback">
            <h2 class="section-title">學生回饋與作品</h2>
            <div class="list-container" style="padding: 30px;">
                {feedback_content}
            </div>
        </section>
    </div>

    <!-- 頁尾 -->
    <footer class="footer">
        <p>© 2026 {name}. All rights reserved.</p>
        <p>Powered by Python Automatic Builder & GitHub Pages.</p>
    </footer>

    <!-- 圖片燈箱 JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const images = document.querySelectorAll('.gallery-trigger, .about-section img, .post-content img');
            if (images.length === 0) return;

            const lightbox = document.createElement('div');
            lightbox.id = 'lightbox';
            lightbox.className = 'lightbox-modal';
            lightbox.innerHTML = `
                <span class="lightbox-close">&times;</span>
                <img class="lightbox-content" src="" alt="放大圖片">
            `;
            document.body.appendChild(lightbox);

            const lightboxImg = lightbox.querySelector('.lightbox-content');
            const closeBtn = lightbox.querySelector('.lightbox-close');

            const closeLightbox = () => {{
                lightbox.classList.remove('active');
                setTimeout(() => {{
                    lightbox.style.display = 'none';
                }}, 300);
            }};

            images.forEach(img => {{
                if (img.closest('a')) return;
                img.style.cursor = 'zoom-in';
                img.addEventListener('click', () => {{
                    lightboxImg.src = img.src;
                    lightboxImg.alt = img.alt || '放大圖片';
                    lightbox.style.display = 'flex';
                    lightbox.offsetHeight; // force reflow
                    lightbox.classList.add('active');
                }});
            }});

            closeBtn.addEventListener('click', closeLightbox);
            lightbox.addEventListener('click', (e) => {{
                if (e.target === lightbox) closeLightbox();
            }});
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape' && lightbox.classList.contains('active')) closeLightbox();
            }});
        }});
    </script>

    <!-- 分類篩選 JavaScript -->
    <script>
        function filterLessons(btn) {{
            document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filter = btn.dataset.filter;
            const items = document.querySelectorAll('#lessonList .list-item');
            let visible = 0;
            items.forEach(item => {{
                const cats = (item.dataset.categories || '').split(',').map(s => s.trim());
                const show = filter === 'all' || cats.includes(filter);
                if (show) {{
                    item.style.display = '';
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(8px)';
                    requestAnimationFrame(() => {{
                        item.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }});
                    visible++;
                }} else {{
                    item.style.display = 'none';
                }}
            }});
            document.getElementById('lessonVisibleCount').textContent = visible;
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            const items = document.querySelectorAll('#lessonList .list-item');
            const counts = {{ all: 0 }};
            items.forEach(item => {{
                counts.all++;
                const cats = (item.dataset.categories || '').split(',').map(s => s.trim());
                cats.forEach(cat => {{ if (cat) counts[cat] = (counts[cat] || 0) + 1; }});
            }});
            document.getElementById('lessonVisibleCount').textContent = counts.all;
            document.querySelectorAll('.filter-chip').forEach(btn => {{
                const n = counts[btn.dataset.filter];
                if (n !== undefined) {{
                    const badge = document.createElement('span');
                    badge.className = 'chip-count';
                    badge.textContent = n;
                    btn.appendChild(badge);
                }}
            }});
        }});
    </script>

</body>
</html>
"""

# HTML 範本：文章詳細頁 post.html
# 使用 {css_path} 和 {home_path} 動態處理子資料夾的相對路徑
POST_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post_title} | {site_name}</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>

    <!-- 頂部導覽列 (毛玻璃效果) -->
    <nav class="navbar">
        <div class="navbar-container">
            <a href="{home_path}" class="navbar-brand">{site_name}</a>
            <ul class="navbar-links">
                <li><a href="{home_path}">返回首頁</a></li>
                <li><a href="{home_path}#projects">精選作品</a></li>
                <li><a href="{home_path}#lessons">教學文章</a></li>
                <li><a href="{home_path}#resources">學習資源</a></li>
            </ul>
        </div>
    </nav>

    <div class="container">
        <article class="post-detail" style="background-color: var(--card-bg); padding: 40px; border-radius: 18px; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); margin-top: 20px;">
            <header class="post-header">
                <h1 class="post-title">{post_title}</h1>
                <div class="post-meta">
                    <span>📅 發布日期: {post_date}</span>
                    <span>🏷️ 分類: {post_category}</span>
                </div>
            </header>
            
            <div class="post-content">
                {post_content}
            </div>
            
            <div style="margin-top: 40px; border-top: 1px solid var(--border-color); padding-top: 20px;">
                <a href="{home_path}#lessons" class="btn btn-primary">← 返回文章列表</a>
            </div>
        </article>
    </div>

    <!-- 頁尾 -->
    <footer class="footer">
        <p>© 2026 {site_name}. All rights reserved.</p>
    </footer>

    <!-- 圖片燈箱 JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const images = document.querySelectorAll('.gallery-trigger, .about-section img, .post-content img');
            if (images.length === 0) return;

            const lightbox = document.createElement('div');
            lightbox.id = 'lightbox';
            lightbox.className = 'lightbox-modal';
            lightbox.innerHTML = `
                <span class="lightbox-close">&times;</span>
                <img class="lightbox-content" src="" alt="放大圖片">
            `;
            document.body.appendChild(lightbox);

            const lightboxImg = lightbox.querySelector('.lightbox-content');
            const closeBtn = lightbox.querySelector('.lightbox-close');

            const closeLightbox = () => {{
                lightbox.classList.remove('active');
                setTimeout(() => {{
                    lightbox.style.display = 'none';
                }}, 300);
            }};

            images.forEach(img => {{
                if (img.closest('a')) return;
                img.style.cursor = 'zoom-in';
                img.addEventListener('click', () => {{
                    lightboxImg.src = img.src;
                    lightboxImg.alt = img.alt || '放大圖片';
                    lightbox.style.display = 'flex';
                    lightbox.offsetHeight; // force reflow
                    lightbox.classList.add('active');
                }});
            }});

            closeBtn.addEventListener('click', closeLightbox);
            lightbox.addEventListener('click', (e) => {{
                if (e.target === lightbox) closeLightbox();
            }});
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape' && lightbox.classList.contains('active')) closeLightbox();
            }});
        }});
    </script>

</body>
</html>
"""

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("開始編譯個人教學網站...")

    # 1. 讀取並解析關於我 (about/profile.md)
    about_path = os.path.join(base_dir, 'about', 'profile.md')
    if not os.path.exists(about_path):
        print("錯誤: 找不到 'about/profile.md' 檔案！")
        return
        
    with open(about_path, 'r', encoding='utf-8') as f:
        about_data = f.read()
    
    about_meta, about_body = parse_front_matter(about_data)
    about_html = markdown.markdown(about_body)
    
    name = about_meta.get('name', '老師')
    title = about_meta.get('title', '程式啟蒙導師')
    email = about_meta.get('email', '')
    github = about_meta.get('github', '')

    # 2. 讀取並解析精選作品 (projects/*.md)
    projects_dir = os.path.join(base_dir, 'projects')
    project_cards = []
    
    if os.path.exists(projects_dir):
        for filename in sorted(os.listdir(projects_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(projects_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    p_data = f.read()
                
                p_meta, _ = parse_front_matter(p_data)
                p_title = p_meta.get('title', '無標題作品')
                p_summary = p_meta.get('summary', '')
                p_date = p_meta.get('date', '')
                p_link = p_meta.get('link', '#')
                p_tags = p_meta.get('tags', [])
                
                tags_html = "".join([f'<span class="card-tag" style="margin-right: 8px;">#{tag}</span>' for tag in p_tags])
                
                card_html = f"""
                <div class="card">
                    <div>
                        <div style="margin-bottom: 8px;">{tags_html}</div>
                        <h3 class="card-title">{p_title}</h3>
                        <p class="card-desc">{p_summary}</p>
                    </div>
                    <div>
                        <div class="card-date" style="margin-bottom: 12px;">📅 {p_date}</div>
                        <a href="{p_link}" target="_blank" class="btn btn-primary" style="display: block; font-size: 12px;">瀏覽作品 ›</a>
                    </div>
                </div>
                """
                project_cards.append(card_html)
                
    project_cards_html = "\n".join(project_cards) if project_cards else "<p>目前尚無作品展示。</p>"

    # 3. 讀取教學資源與學生回饋 (resources/recommendations.md, student_works/feedback.md)
    resources_path = os.path.join(base_dir, 'resources', 'recommendations.md')
    resources_html = ""
    if os.path.exists(resources_path):
        with open(resources_path, 'r', encoding='utf-8') as f:
            res_meta, res_body = parse_front_matter(f.read())
            resources_html = markdown.markdown(res_body)
    else:
        resources_html = "<p>目前尚無推薦資源。</p>"

    feedback_path = os.path.join(base_dir, 'student_works', 'feedback.md')
    feedback_html = ""
    if os.path.exists(feedback_path):
        with open(feedback_path, 'r', encoding='utf-8') as f:
            feed_meta, feed_body = parse_front_matter(f.read())
            feedback_html = markdown.markdown(feed_body)
    else:
        feedback_html = "<p>目前尚無學生回饋。</p>"

    # 4. 讀取、解析並生成教學文章 (lessons/**/*.md，支援子資料夾)
    #    同一篇文章若出現在多個子資料夾，以「第一次出現」的路徑為主，
    #    但把所有出現過的分類合併到 data-categories，篩選時都能找到。
    lessons_dir = os.path.join(base_dir, 'lessons')
    parenting_list = []

    # 收集所有 .md 檔案（含子資料夾）
    all_md_files = []
    if os.path.exists(lessons_dir):
        for dirpath, dirnames, filenames in os.walk(lessons_dir):
            filenames.sort(reverse=True)
            for filename in filenames:
                if filename.endswith('.md'):
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, lessons_dir)
                    all_md_files.append((full_path, rel_path, filename))

    # 按檔名降序排序（讓日期越新的越前面）
    all_md_files.sort(key=lambda x: x[2], reverse=True)

    # 去重字典：filename → {html_path, title, date, category_label, categories: set}
    article_map = {}   # 用於去重，key = filename
    article_order = [] # 保持排序

    for full_path, rel_path, filename in all_md_files:
        with open(full_path, 'r', encoding='utf-8') as f:
            l_data = f.read()

        l_meta, l_body = parse_front_matter(l_data)
        l_title    = l_meta.get('title', '無標題文章')
        l_date     = l_meta.get('date', '') or '未知日期'
        l_category = l_meta.get('category', '一般')

        # 從子資料夾名稱推斷分類
        parts = rel_path.replace('\\', '/').split('/')
        subfolder_cat = parts[0] if len(parts) > 1 else l_category

        # 計算 CSS 相對路徑
        depth = len(parts)
        up = '../' * depth

        # 生成 HTML 檔（無論是否重複，每個子資料夾的 HTML 都要生成）
        content_html = markdown.markdown(l_body, extensions=['extra', 'nl2br'])
        html_filename = filename.replace('.md', '.html')
        html_filepath = os.path.join(os.path.dirname(full_path), html_filename)
        rel_html = os.path.relpath(html_filepath, base_dir).replace('\\', '/')

        rendered_post = POST_TEMPLATE.format(
            site_name=name,
            post_title=l_title,
            post_date=l_date,
            post_category=l_category,
            post_content=content_html,
            css_path=f"{up}assets/css/style.css",
            home_path=f"{up}index.html",
        )
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_post)
        safe_print(f"  生成: {rel_html}")

        # 去重：同一 filename 只在首頁列表出現一次
        if filename not in article_map:
            article_map[filename] = {
                'html_path': rel_html,
                'title': l_title,
                'date': l_date,
                'category_label': l_category,
                'categories': {subfolder_cat},
                'is_parenting': (l_category == '親職教育'),
            }
            article_order.append(filename)
        else:
            # 已存在 → 補上這個分類
            article_map[filename]['categories'].add(subfolder_cat)
            # 若這次找到日期而之前沒有，更新
            if l_date != '未知日期' and article_map[filename]['date'] == '未知日期':
                article_map[filename]['date'] = l_date

    # 依排序建立首頁列表 HTML
    lessons_list = []
    for fname in article_order:
        info = article_map[fname]
        cats_str = ','.join(sorted(info['categories']))  # e.g. "iPad教學,說數學"
        rel_html = info['html_path']
        l_title = info['title']
        l_date = info['date']
        l_category = info['category_label']

        if info['is_parenting']:
            parenting_item_html = f"""
                    <div class="list-item" data-categories="{cats_str}">
                        <div class="list-item-content">
                            <span style="font-size: 11px; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{l_category} (網路資源整理)</span>
                            <a href="{rel_html}" class="list-item-title" style="font-weight: 600; font-size: 17px; margin-top: 4px;">{l_title}</a>
                            <span class="list-item-date">📅 {l_date}</span>
                        </div>
                        <a href="{rel_html}" class="btn btn-link">瀏覽圖卡</a>
                    </div>"""
            parenting_list.append(parenting_item_html)
        else:
            list_item_html = f"""
                    <div class="list-item" data-categories="{cats_str}">
                        <div class="list-item-content">
                            <span class="item-category-tag">{l_category}</span>
                            <a href="{rel_html}" class="list-item-title" style="font-weight: 600; font-size: 17px; margin-top: 4px;">{l_title}</a>
                            <span class="list-item-date">📅 {l_date}</span>
                        </div>
                        <a href="{rel_html}" class="btn btn-link">閱讀全文</a>
                    </div>"""
            lessons_list.append(list_item_html)

    lesson_list_html = "\n".join(lessons_list) if lessons_list else "<p>目前尚無教學文章。</p>"
    parenting_list_html = "\n".join(parenting_list) if parenting_list else "<p>目前尚無親職教養資源。</p>"

    # 5. 渲染並輸出首頁 index.html
    rendered_index = INDEX_TEMPLATE.format(
        site_name=name,
        name=name,
        title=title,
        email=email,
        github=github,
        about_content=about_html,
        project_cards=project_cards_html,
        lesson_list=lesson_list_html,
        parenting_list=parenting_list_html,
        resources_content=resources_html,
        feedback_content=feedback_html
    )

    index_path = os.path.join(base_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(rendered_index)
        
    print("成功生成首頁: index.html")
    print("網站建置完成！您可以在瀏覽器中打開 index.html 預覽您的 Apple 風格教學網站。")

if __name__ == '__main__':
    main()
