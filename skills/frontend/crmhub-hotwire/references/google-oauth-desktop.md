# Google OAuth for Desktop Apps (Rails + OmniAuth)

## When to Use

For a Rails desktop-style app where multiple users share the same machine, Google OAuth lets each user sign in with their own Google account. Each person clicks "Sign in with Google", Google's OAuth popup asks for THEIR credentials, and the app links that Google identity to a CRM Hub user record.

## Setup Requirements

### 1. Google Cloud Project + OAuth Desktop Client

```bash
# Create project
gcloud projects create crm-hub-saas --name="CRM Hub SaaS"

# Enable required APIs
gcloud services enable people.googleapis.com --project=crm-hub-saas
gcloud services enable plus.googleapis.com --project=crm-hub-saas

# Create OAuth Desktop client (via Console UI — gcloud CLI doesn't support this directly)
# Go to: https://console.cloud.google.com/apis/credentials?project=crm-hub-saas
# → + CREATE CREDENTIALS → OAuth client ID → Desktop app
# → Name: "CRM Hub Desktop"
# → Copy Client ID and Client Secret
```

**Note:** `gcloud` CLI cannot create OAuth client credentials directly. You MUST use the Google Cloud Console web UI for this step. The `gcloud alpha services oauth` commands are limited and don't cover OAuth client creation.

### 2. Store Credentials Securely

Store in `~/.openclaw/credentials/google-oauth.json` (NOT committed to git):

```json
{
  "client_id": "xxxxxxxx.apps.googleusercontent.com",
  "client_secret": "xxxxxxxxxxxxxxxx"
}
```

### 3. Rails Configuration

**Gemfile:**
```ruby
gem 'omniauth-google-oauth2'
gem 'omniauth-rails_csrf_protection' # Required for Rails 7+
```

**config/initializers/omniauth.rb:**
```ruby
Rails.application.config.middleware.use OmniAuth::Builder do
  provider :google_oauth2,
    Rails.application.credentials.dig(:google, :client_id),
    Rails.application.credentials.dig(:google, :client_secret),
    {
      scope: 'email,profile',
      prompt: 'select_account',  # Forces account picker — critical for shared desktop
      image_aspect_ratio: 'square',
      image_size: 96
    }
end
```

**Critical:** `prompt: 'select_account'` forces Google to show the account picker every time. Without this, Google auto-signs-in with the last account — bad for shared desktops.

### 4. Routes

```ruby
# config/routes.rb
devise_for :users, controllers: { omniauth_callbacks: 'users/omniauth_callbacks' }
```

### 5. OmniAuth Callback Controller

```ruby
# app/controllers/users/omniauth_callbacks_controller.rb
class Users::OmniauthCallbacksController < Devise::OmniauthCallbacksController
  def google_oauth2
    @user = User.from_omniauth(request.env['omniauth.auth'])

    if @user.persisted?
      sign_in_and_redirect @user, event: :authentication
      set_flash_message(:notice, :success, kind: 'Google') if is_navigational_format?
    else
      session['devise.google_data'] = request.env['omniauth.auth'].except(:extra)
      redirect_to new_user_registration_path, alert: @user.errors.full_messages.join("\n")
    end
  end

  def failure
    redirect_to root_path, alert: 'Authentication failed. Please try again.'
  end
end
```

### 6. User Model

```ruby
# app/models/user.rb
class User < ApplicationRecord
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable,
         :omniauthable, omniauth_providers: [:google_oauth2]

  def self.from_omniauth(auth)
    where(provider: auth.provider, uid: auth.uid).first_or_create do |user|
      user.email = auth.info.email
      user.password = Devise.friendly_token[0, 20]
      user.name = auth.info.name
      # Link to existing account by email if user already exists
    end
  end
end
```

### 7. Migration

```bash
rails generate migration AddOmniauthToUsers provider:string uid:string
rails db:migrate
```

### 8. Redirect URI

In Google Cloud Console, add authorized redirect URI:
- Development: `http://localhost:3000/users/auth/google_oauth2/callback`
- Production: `https://your-domain.com/users/auth/google_oauth2/callback`

## Multi-User Desktop Considerations

1. **Always use `prompt: 'select_account'`** — forces account picker, prevents auto-login with wrong account
2. **Prominent "Sign out" button** — users must be able to switch accounts easily
3. **Link by email** — if `owner@glowhair.com` exists as a password user AND as a Google account, link them
4. **Session timeout** — shorter sessions on shared machines (30 min default)

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `redirect_uri_mismatch` | Redirect URI not registered in Console | Add exact URI to authorized redirect URIs |
| `invalid_client` | Wrong client ID/secret | Regenerate in Console, update credentials |
| `access_denied` | User cancelled OAuth | Normal — redirect back to sign-in |
| `CSRF detected` | Missing CSRF token | Ensure `omniauth-rails_csrf_protection` gem is installed |
