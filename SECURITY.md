# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to:

**security@ethys.dev**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

When using this package:

1. **Never commit private keys or API keys** to version control
2. **Use environment variables** or secure secret management systems
3. **Avoid logging sensitive data** (addresses, signatures, keys)
4. **Review contract approvals** - use specific amounts, not unlimited
5. **Keep dependencies updated** - regularly update to latest versions
6. **Use wallet-signed authentication** - preferred over API keys

## Disclosure Policy

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide an estimated timeline for a fix
- We will notify you when the vulnerability is fixed
- We will credit you in the security advisory (unless you prefer to remain anonymous)

