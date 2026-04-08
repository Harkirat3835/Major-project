# Login Process Rewrite - Progress Tracker

## Status: [IN PROGRESS] 12/22 steps completed

### Phase 1: Backend Security & Models (✓ 8/8 complete)

### Phase 2: Password Reset Flow (Steps 9-11)
- [ ] 9. Add /api/auth/forgot-password: Generate reset token, send email
- [ ] 10. Add /api/auth/reset-password: Validate token, update password
- [ ] 11. Update User model methods: is_locked(), increment_failed_login(), reset_failed_logins()

### Phase 3: Frontend Updates (Steps 12-18)
- [ ] 12. Update frontend/src/pages/Auth.tsx: Password validation, separate register flow
- [ ] 13. Update frontend/src/contexts/AuthContext.tsx: Refresh token logic
- [ ] 14. Implement frontend/src/pages/ForgotPassword.tsx: Full forgot flow
- [ ] 15. Implement frontend/src/pages/ResetPassword.tsx: Full reset flow

### Phase 4: Dependencies & Testing (Steps 19-22)
- [x] 19. Update requirements.txt: Add flask-mail, etc. + pip install


### Phase 1: Backend Security & Models (Steps 1-8)
- [x] 1. Update app/models.py: Add new User fields (failed_logins, locked_until, email_verified, refresh_token_hash, email_verification_token, password_reset_token)
- [x] 2. Update app/config.py: Add MAIL settings, password policy constants, JWT_REFRESH_TOKEN_EXPIRES
- [x] 3. Update app/__init__.py: Initialize Flask-Mail, update Limiter for auth
- [x] 4. Add rate limiting decorators to auth routes in app/routes.py
- [x] 5. Rewrite /api/auth/login: Handle lockout, issue access+refresh tokens
- [x] 6. Update /api/auth/register: Generate email_verification_token, don't auto-login
- [x] 7. Add /api/auth/refresh: Rotate refresh tokens
- [x] 8. Add /api/auth/verify-email (GET/POST)

### Phase 1: Backend Security & Models (Steps 1-8)
- [x] 1. Update app/models.py: Add new User fields (failed_logins, locked_until, email_verified, refresh_token_hash, email_verification_token, password_reset_token)
- [x] 2. Update app/config.py: Add MAIL settings, password policy constants, JWT_REFRESH_TOKEN_EXPIRES
- [x] 3. Update app/__init__.py: Initialize Flask-Mail, update Limiter for auth
- [x] 4. Add rate limiting decorators to auth routes in app/routes.py
- [x] 5. Rewrite /api/auth/login: Handle lockout, issue access+refresh tokens
- [x] 6. Update /api/auth/register: Generate email_verification_token, don't auto-login
- [x] 7. Add /api/auth/refresh: Rotate refresh tokens


### Phase 1: Backend Security & Models (Steps 1-8)
- [ ] 1. Update app/models.py: Add new User fields (failed_logins, locked_until, email_verified, refresh_token_hash, email_verification_token, password_reset_token)
- [ ] 2. Update app/config.py: Add MAIL settings, password policy constants, JWT_REFRESH_TOKEN_EXPIRES
- [ ] 3. Update app/__init__.py: Initialize Flask-Mail, update Limiter for auth
- [ ] 4. Add rate limiting decorators to auth routes in app/routes.py
- [ ] 5. Rewrite /api/auth/login: Handle lockout, issue access+refresh tokens
- [ ] 6. Update /api/auth/register: Generate email_verification_token, don't auto-login
- [ ] 7. Add /api/auth/refresh: Rotate refresh tokens
- [ ] 8. Add /api/auth/verify-email (GET/POST)

### Phase 2: Password Reset Flow (Steps 9-11)
- [ ] 9. Add /api/auth/forgot-password: Generate reset token, send email
- [ ] 10. Add /api/auth/reset-password: Validate token, update password
- [ ] 11. Update User model methods: is_locked(), increment_failed_login(), reset_failed_logins()

### Phase 3: Frontend Updates (Steps 12-18)
- [ ] 12. Update frontend/src/pages/Auth.tsx: Password validation, separate register flow
- [ ] 13. Update frontend/src/contexts/AuthContext.tsx: Refresh token logic
- [ ] 14. Implement frontend/src/pages/ForgotPassword.tsx: Full forgot flow
- [ ] 15. Implement frontend/src/pages/ResetPassword.tsx: Full reset flow
- [ ] 16. Create/update frontend/src/lib/api.ts: Axios interceptor for refresh
- [ ] 17. Update Navbar.tsx: Protect routes if unauth
- [ ] 18. Add protected route wrapper in App.tsx

### Phase 4: Dependencies & Testing (Steps 19-22)
- [ ] 19. Update requirements.txt: Add flask-mail, etc. + pip install
- [ ] 20. Update run.py: Ensure new init
- [ ] 21. Add DB migration (manual SQL or Alembic)
- [ ] 22. Update tests/test_app.py + run tests + E2E

**Next command:** `python run.py` to test backend. `cd frontend && npm run dev` for FE.

**Demo users:** admin@truthguard.ai / Admin@1234 (after migration).

**Notes:** Update .env with mail settings. Rate limit: 5 login/min/IP.

