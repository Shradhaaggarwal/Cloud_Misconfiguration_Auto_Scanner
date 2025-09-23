# Security Policy

## Supported Versions

We actively support the following versions of the Cloud Misconfiguration Auto Scanner:

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | ✅ Full support    |
| 1.1.x   | ✅ Security fixes  |
| 1.0.x   | ❌ End of life     |
| < 1.0   | ❌ Not supported   |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow responsible disclosure:

### 🚨 **DO NOT** create a public GitHub issue for security vulnerabilities

Instead, please email security reports to: **security@[domain-placeholder]**

### What to include in your report:

1. **Vulnerability Description**
   - Clear description of the security issue
   - Affected components/versions
   - Attack vectors and exploitation methods

2. **Impact Assessment**
   - Potential consequences of the vulnerability
   - Risk level assessment (Critical, High, Medium, Low)
   - Affected user types or scenarios

3. **Reproduction Steps**
   - Detailed steps to reproduce the vulnerability
   - Sample payloads or proof-of-concept code
   - Environment details where applicable

4. **Suggested Remediation**
   - Proposed fixes or mitigations (if known)
   - Workarounds for users
   - Additional security improvements

### Our Response Process:

1. **Acknowledgment**: We'll confirm receipt within **48 hours**
2. **Initial Response**: Detailed response within **72 hours**
3. **Investigation**: Thorough security analysis and validation
4. **Fix Development**: Patch creation and testing
5. **Coordinated Disclosure**: Public disclosure after fix deployment

### Timeline:

- **Critical vulnerabilities**: Patches within 7 days
- **High severity**: Patches within 14 days  
- **Medium/Low severity**: Patches in next regular release

## Security Best Practices

### For Users:

1. **Credential Management**
   - Never commit Azure credentials to version control
   - Use Azure Key Vault for production deployments
   - Rotate service principal secrets regularly
   - Apply principle of least privilege

2. **Network Security**
   - Run the scanner from secure networks
   - Use VPNs for remote access
   - Implement network segmentation

3. **Data Protection**
   - Encrypt sensitive scan results
   - Secure database files with appropriate permissions
   - Regularly backup and test recovery procedures

4. **Access Control**
   - Limit scanner access to authorized personnel
   - Use strong authentication mechanisms
   - Monitor and audit scanner usage

### For Developers:

1. **Code Security**
   - Validate all user inputs
   - Use parameterized queries for database operations
   - Implement proper error handling without information disclosure
   - Regular security code reviews

2. **Dependency Management**
   - Keep all dependencies up to date
   - Monitor for known vulnerabilities
   - Use dependency scanning tools

3. **Secret Management**
   - Never hardcode credentials or sensitive data
   - Use environment variables or secure vaults
   - Implement proper secret rotation

## Common Security Considerations

### Azure Permissions

The scanner requires minimal Azure permissions to function:

**Recommended Permissions:**
- `Reader` role at subscription or resource group level
- Custom roles with specific read permissions for enhanced security

**Avoid Granting:**
- `Contributor` or `Owner` roles
- Write permissions unless absolutely necessary
- Global administrator privileges

### Database Security

- SQLite database files should be protected with filesystem permissions
- Consider encrypting database at rest for sensitive environments
- Implement proper backup encryption and access controls

### Network Communications

- All Azure API communications use HTTPS/TLS
- Implement network monitoring for unusual traffic patterns
- Consider using Azure Private Endpoints for enhanced security

## Security Updates

We regularly release security updates and encourage users to:

1. **Subscribe to Notifications**
   - Watch this repository for security releases
   - Follow our security announcements

2. **Update Promptly**
   - Apply security patches as soon as possible
   - Test updates in non-production environments first

3. **Security Scanning**
   - Regularly scan for vulnerabilities in dependencies
   - Use automated security monitoring tools

## Known Security Considerations

### Current Limitations:

1. **Local Database Storage**: SQLite database stored locally may contain sensitive findings
2. **Memory Exposure**: Scan results temporarily stored in application memory
3. **Log Files**: Debug logs may contain sensitive resource information

### Mitigation Strategies:

1. Run scanner in secure, isolated environments
2. Implement proper log rotation and sanitization
3. Use encrypted storage for database files
4. Regular security assessments of deployment environment

## Security Research and Bug Bounty

We welcome security research and responsible disclosure. While we don't currently offer a formal bug bounty program, we recognize valuable security contributions through:

- Public acknowledgment (with permission)
- Contribution credits in release notes
- Collaboration opportunities

## Contact Information

For security-related questions or concerns:

- **Security Team**: security@[domain-placeholder]
- **General Security Questions**: Create a private discussion
- **Emergency Security Issues**: Use email for immediate attention

---

**Note**: This security policy may be updated periodically. Please check back regularly for the latest information.