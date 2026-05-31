from flask import Flask, render_template
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def test():
    # Check the template path
    print("Template loader:", app.jinja_loader)
    print("Template paths:", app.jinja_loader.searchpath if hasattr(app.jinja_loader, 'searchpath') else 'N/A')
    
    # Read the file directly
    with open('templates/dashboard.html', 'r') as f:
        content = f.read()
        has_class = 'class="action-btn primary"' in content
        print(f"File on disk has class: {has_class}")
        if 'id="scanBtn"' in content:
            idx = content.find('id="scanBtn"')
            print(f"File content at scanBtn: {content[idx:idx+100]}")
    
    # Render via Flask
    result = render_template('dashboard.html')
    has_class_rendered = 'class="action-btn primary"' in result
    print(f"Rendered result has class: {has_class_rendered}")
    if 'id="scanBtn"' in result:
        idx = result.find('id="scanBtn"')
        print(f"Rendered content at scanBtn: {result[idx:idx+100]}")
    
    return result

if __name__ == '__main__':
    app.run(port=8000, debug=False)
