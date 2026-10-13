# Preliminary Plan v1.0

## BlueSky Firehose Sampling Project

### Project Purpose
Learning project to understand BlueSky firehose mechanics by simulating real-time traffic from an existing feed. Focus on simplest pieces first with rapid prototyping.

### Design Principles (per DEVELOPMENT.md)
- Concise, readable, opinionated code
- Brevity paramount
- Support a few common workflows
- No sprawling configuration

### Key Decisions

**1. Sampling Strategy**
- Simulate real-time traffic from existing feed
- Configurable sampling parameters
- Initial testing: very small sample (tiny fraction of posts)
- Content focus: Posts only (not all firehose events)

**2. Data Volume**
- **Initial testing target**: 3 posts (rapid prototyping)
- **Planning scale**: 1M messages (not implemented in this learning project)
- **Vision**: Ongoing monitoring capability (design for this, but don't implement)

**3. Authentication**
- Read-only access without authentication
- Leverage public firehose access
- No credential management needed for this project

**4. Output Format**
- JSON format (current implementation)
- Storage location: `data/incoming/firehose/latest/`
- File size limit: 10MB per file
- **Future consideration**: Database layer (planning only, not implemented)
- Data will be read/processed within this project

### Technical Considerations

**Scope for Learning Project**:
- ✓ Simple firehose connection
- ✓ Basic post filtering
- ✓ Configurable sampling
- ✓ JSON file output
- ✓ File size management (10MB limit)
- Output format optimization

**Future Enhancements (Planning Only)**:
- Database integration layer
- Ongoing monitoring mode
- Scale to 1M+ messages
- Scale to 1B+ messages
- Scale to 1T+ messages
- Advanced filtering/analysis


### Next Steps

1. Research BlueSky firehose public endpoint
2. Choose minimal dependencies (WebSocket client)
3. Create `data/incoming/firehose/latest/` directory structure
4. Implement basic connection and capture 3 posts
5. Add configurable sampling parameters
6. Implement 10MB file rotation (update: put this on hold for now, it's low priority)
