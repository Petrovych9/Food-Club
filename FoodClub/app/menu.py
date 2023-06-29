from flask import url_for
def menu():
    menu = {
        'Home': url_for('main.home'),
        'All recipes': url_for('main.all_recipes'),
        'New recipe': url_for('main.new_recipe'),
        'My drafts': url_for('main.draft_recipes'),
        'Profile': url_for('main.profile'),
        'Sign In': url_for('auth.signin'),
        'Log out': url_for('auth.logout'),
        'Sign Up': url_for('auth.signup')
    }
    return menu