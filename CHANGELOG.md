# Changelog

All notable changes to the Cloud Misconfiguration Auto Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Multi-cloud support (AWS, GCP)
- Advanced PDF/HTML reporting with executive summaries
- GenAI integration for finding explanations
- REST API endpoints
- Custom security rules engine
- Webhook notifications
- Compliance framework mappings (CIS, NIST, SOC2)

## [1.2.0] - 2025-01-XX

### Added
- Comprehensive documentation suite (README, CONTRIBUTING, SECURITY)
- Professional project branding and structure
- Environment configuration templates
- MIT License for open source distribution
- Security policy and responsible disclosure process

### Enhanced
- Improved README with detailed installation and usage instructions
- Professional project structure documentation
- Code contribution guidelines and workflow
- Architecture diagrams and feature descriptions

### Documentation
- Complete API documentation for all scanner modules
- Development setup and testing procedures
- Security best practices and guidelines
- Professional contributor onboarding process

## [1.1.0] - 2024-12-XX (Estimated)

### Added
- **Streamlit Web Interface**: Modern web-based UI with interactive dashboard
- **SQLite Database Integration**: Persistent storage for scan results and history
- **Multi-threaded Scanning**: Parallel execution of security checks for improved performance
- **Advanced Findings Explorer**: Filterable and searchable security findings table
- **Dashboard Analytics**: Visual charts and KPIs for security posture assessment
- **Database Browser**: Raw data inspection capabilities

### Enhanced
- **Improved Error Handling**: Better exception management and user feedback
- **Performance Optimizations**: Faster scanning through concurrent execution
- **User Experience**: Intuitive navigation and professional UI design
- **Data Persistence**: Historical trend analysis capabilities

### Fixed
- Memory optimization issues during large-scale scans
- UI responsiveness problems with large datasets
- Database connection handling improvements

## [1.0.0] - 2024-11-XX (Estimated)

### Added
- **Core Azure Security Scanning**:
  - Storage Account public blob access detection
  - Virtual Machine public IP identification  
  - Network Security Group rule analysis
- **Command Line Interface**: Basic CLI scanning capabilities
- **Azure SDK Integration**: Complete Azure resource inventory and analysis
- **Security Findings Database**: Initial SQLite-based findings storage
- **Basic Reporting**: JSON-formatted scan results output

### Security Checks Implemented
- `AZ-Storage-PublicBlob-001`: Detect storage accounts with public blob access
- `AZ-VM-PUBIP-001`: Identify VMs with public IP addresses
- `AZ-NSG-OPEN-001`: Flag overly permissive NSG rules

### Infrastructure
- **Azure Service Principal Authentication**: Secure Azure API access
- **Environment Configuration**: `.env` based configuration management
- **Error Handling**: Basic exception management and logging
- **Database Models**: SQLAlchemy-based data models for findings storage

## [0.1.0] - 2024-10-XX (Initial Development)

### Added
- Project initialization and basic structure
- Azure SDK integration proof of concept
- Initial security check framework
- Development environment setup

---

## Version History Summary

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **1.2.0** | 2025-01-XX | Professional documentation, security policy |
| **1.1.0** | 2024-12-XX | Web UI, database persistence, multi-threading |
| **1.0.0** | 2024-11-XX | Core scanning engine, CLI interface |
| **0.1.0** | 2024-10-XX | Initial development, proof of concept |

## Migration Guides

### Upgrading to v1.2.0 from v1.1.0
- No breaking changes
- Enhanced documentation and security guidelines
- New environment configuration templates available

### Upgrading to v1.1.0 from v1.0.0
- Web interface available at `http://localhost:8501` after running `streamlit run app.py`
- Database schema automatically migrated
- All previous CLI functionality preserved

### Upgrading to v1.0.0 from v0.1.0
- Complete rewrite with improved architecture
- New configuration format required (see `.env.example`)
- Enhanced security check accuracy and coverage

## Breaking Changes

### v1.0.0
- **Configuration Format**: Changed from JSON to environment variables
- **Database Schema**: New SQLAlchemy-based models (auto-migration included)
- **API Changes**: Updated function signatures for security checks

## Security Updates

### v1.2.0
- Enhanced security documentation and best practices
- Responsible disclosure policy established
- Security-focused contribution guidelines

### v1.1.0
- Improved credential handling in web interface
- Enhanced database security with connection pooling
- Input validation improvements

### v1.0.0
- Secure Azure credential management
- SQL injection prevention through parameterized queries
- Sensitive data handling improvements

## Known Issues

### Current (v1.2.0)
- None reported

### v1.1.0
- Large datasets (>10,000 findings) may cause UI performance issues
- Streamlit session state occasionally resets during long scans
- **Workaround**: Use CLI interface for very large environments

### v1.0.0
- **Fixed in v1.1.0**: CLI output formatting inconsistent with special characters
- **Fixed in v1.1.0**: Memory usage grows significantly with large scan results

## Contributors

Special thanks to all contributors who helped make this project possible:

- **Anirudh Dattu** - Project Creator and Lead Maintainer
- **Community Contributors** - Bug reports, feature requests, and improvements

## Support and Compatibility

### Python Versions
- **v1.2.0+**: Python 3.8+ (3.12 recommended)
- **v1.1.0**: Python 3.8+
- **v1.0.0**: Python 3.8+

### Azure SDK Versions
- **v1.2.0+**: Latest Azure SDK packages (2024+ versions)
- **v1.1.0**: Azure SDK 2023+ versions
- **v1.0.0**: Azure SDK 2023 versions

### Operating System Support
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+
- CentOS 7+
- Docker containers (Alpine Linux)

---

*For more information about any release, please see the corresponding GitHub release notes and documentation.*