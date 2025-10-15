# LinkedIn Automation Agent

An intelligent AI-powered agent that automates LinkedIn posting and engagement activities. The agent operates twice weekly (Wednesdays and Saturdays) from 9:00 AM to 10:00 AM, intelligently engaging with your top 50 connections and posting high-quality content generated using Perplexity AI.

## Features

- **Automated Scheduling**: Runs twice weekly on Wednesdays and Saturdays (9:00-10:00 AM)
- **Intelligent Engagement**: Engages with top 50 connections' posts before and after your main post
- **AI-Generated Content**: Uses Perplexity AI to generate professional LinkedIn posts and comments
- **Rate Limiting**: Built-in protection against LinkedIn rate limits
- **Comprehensive Logging**: Detailed activity logs and monitoring
- **Secure Configuration**: Safe API key management with environment variables
- **Flexible Topics**: Easy weekly topic management system

## System Requirements

- Python 3.7 or higher
- Windows/Linux/macOS
- Internet connection
- LinkedIn API access
- Perplexity AI API access

## Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd linkedin-automation-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration:
   ```bash
   cp .env.example .env
   ```

4. **Configure your environment file**
   Edit `.env` with your credentials:
   ```env
   # LinkedIn API Configuration
   LINKEDIN_CLIENT_ID=your_linkedin_client_id
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_USER_ID=your_linkedin_user_id

   # Perplexity AI Configuration
   PERPLEXITY_API_KEY=your_perplexity_api_key

   # Optional Configuration
   TIMEZONE=America/New_York
   LOG_LEVEL=INFO
   ```

## Configuration

### API Keys Setup

#### LinkedIn API
1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new application
3. Get your Client ID and Client Secret
4. Generate an access token with required permissions:
   - `r_liteprofile` (read profile)
   - `w_member_social` (post content)
   - `r_member_social` (read posts)

#### Perplexity AI API
1. Sign up at [Perplexity AI](https://www.perplexity.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

### Weekly Topics Configuration

Set your weekly topics using the topics manager:

```bash
# View current topics
python topics_config.py list

# Set new topics for the week
python topics_config.py set "AI trends" "Remote work productivity" "Leadership insights" "Digital transformation" "Industry analysis"

# Add a single topic
python topics_config.py add "Cybersecurity best practices"

# Remove a topic
python topics_config.py remove "Old topic"

# Get random topics from the pool
python topics_config.py random 5

# Enable auto-rotation of topics
python topics_config.py auto-rotate on
```

## Usage

### Starting the Agent

```bash
python main.py
```

The agent will:
1. Initialize all components
2. Schedule automation tasks for Wednesdays and Saturdays
3. Run continuously, waiting for scheduled times
4. Log all activities to `logs/` directory

### Manual Topic Updates

You can update topics anytime without restarting the agent:

```python
from topics_config import update_topics

# Update topics for current week
topics = [
    "Artificial Intelligence trends",
    "Remote work best practices", 
    "Leadership development",
    "Digital marketing strategies",
    "Business innovation"
]

update_topics(topics)
```

### Monitoring

The agent provides comprehensive logging and monitoring:

- **Activity Logs**: `logs/activity.log`
- **Error Logs**: `logs/error.log`
- **Performance Logs**: `logs/performance.log`

Check system health:
```python
from main import LinkedInAutomationAgent

agent = LinkedInAutomationAgent()
status = agent.get_status()
print(status)
```

## Schedule Details

### Weekly Schedule
- **Days**: Wednesdays and Saturdays
- **Time Window**: 9:00 AM - 10:00 AM (your local timezone)
- **Main Post**: Exactly at 9:30 AM

### Engagement Timeline
- **9:00 - 9:30 AM**: Pre-posting engagement (30 minutes)
  - Engage with top 50 connections' recent posts
  - Like and comment on relevant content
- **9:30 AM**: Publish main LinkedIn post
- **9:30 - 10:00 AM**: Post-posting engagement (30 minutes)
  - Continue engaging with connections
  - Monitor post performance

## Safety Features

### Rate Limiting
- Built-in delays between API calls
- Intelligent throttling to avoid LinkedIn limits
- Exponential backoff on errors

### Error Handling
- Comprehensive error logging
- Automatic retry mechanisms
- Alert system for critical issues
- Graceful degradation on failures

### Security
- Environment variable configuration
- No hardcoded credentials
- Secure API key management
- Activity audit trails

## File Structure

```
linkedin-automation-agent/
├── main.py                 # Main orchestrator
├── config.py              # Configuration management
├── linkedin_client.py     # LinkedIn API client
├── perplexity_client.py   # Perplexity AI client
├── engagement_manager.py  # Engagement logic
├── scheduler.py           # Task scheduling
├── logger_config.py       # Logging system
├── topics_config.py       # Topics management
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README.md             # This file
└── logs/                 # Log files directory
    ├── activity.log
    ├── error.log
    └── performance.log
```

## Troubleshooting

### Common Issues

1. **LinkedIn API Rate Limits**
   - The agent has built-in rate limiting
   - If you hit limits, the agent will wait and retry
   - Check logs for rate limit warnings

2. **Authentication Errors**
   - Verify your LinkedIn API credentials
   - Ensure access token hasn't expired
   - Check API permissions

3. **Perplexity AI Errors**
   - Verify your API key is correct
   - Check your account quota/limits
   - Review error logs for details

4. **Scheduling Issues**
   - Verify your timezone setting
   - Check system clock accuracy
   - Review scheduler logs

### Log Analysis

Check different log files for specific issues:

```bash
# View recent activity
tail -f logs/activity.log

# Check for errors
tail -f logs/error.log

# Monitor performance
tail -f logs/performance.log
```

### Getting Help

1. Check the logs for detailed error messages
2. Verify your configuration in `.env`
3. Test API connections manually
4. Review the topics configuration

## Advanced Configuration

### Custom Scheduling

Modify `config.py` to change scheduling:

```python
# Change posting days (0=Monday, 6=Sunday)
POST_DAYS = [2, 5]  # Wednesday, Saturday

# Change time window
POST_TIME_START = "09:00"
POST_TIME_MAIN = "09:30"
POST_TIME_END = "10:00"
```

### Engagement Settings

Adjust engagement parameters:

```python
# Number of connections to engage with
TOP_CONNECTIONS_COUNT = 50

# Days to look back for posts
POST_LOOKBACK_DAYS = 7

# Comments per session
MAX_COMMENTS_PER_SESSION = 25
```

## Best Practices

1. **Content Quality**: Regularly update your weekly topics to keep content fresh
2. **Monitoring**: Check logs regularly for any issues
3. **Rate Limits**: Don't modify rate limiting settings unless necessary
4. **Topics**: Use diverse, relevant topics for your industry
5. **Engagement**: Let the AI generate natural, contextual comments

## Security Considerations

- Never commit your `.env` file to version control
- Regularly rotate your API keys
- Monitor API usage and costs
- Review generated content before it goes live (if needed)
- Keep the agent updated with latest security patches

## License

This project is for educational and personal use. Please ensure compliance with LinkedIn's Terms of Service and API usage policies.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Verify your configuration
4. Test API connections manually

---

**Note**: This agent is designed to operate autonomously while respecting LinkedIn's rate limits and terms of service. Always monitor its activity and ensure compliance with platform policies.