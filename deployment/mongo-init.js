// ==========================================
// deployment/mongo-init.js
// MongoDB Initialization Script
// ==========================================

// Switch to the agent_reports database
db = db.getSiblingDB('agent_reports');

// Create the daily_report collection with new schema validation
db.createCollection('daily_report', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_input', 'response', 'conversation', 'timestamp'],
      properties: {
        user_input: {
          bsonType: 'string',
          description: 'Original user input/request'
        },
        response: {
          bsonType: 'array',
          description: 'Array of response messages with role and content',
          items: {
            bsonType: 'object',
            required: ['role', 'content'],
            properties: {
              role: {
                bsonType: 'string',
                description: 'Role of the message sender (assistant, user, etc.)'
              },
              content: {
                bsonType: 'string',
                description: 'Content of the message'
              }
            }
          }
        },
        conversation: {
          bsonType: 'object',
          description: 'Structured conversation data from Google Sheets'
        },
        timestamp: {
          bsonType: 'date',
          description: 'Timestamp of the conversation'
        },
        metadata: {
          bsonType: 'object',
          description: 'Additional metadata about the conversation'
        }
      }
    }
  }
});

// Create indexes for better performance
db.daily_report.createIndex({ timestamp: -1 });
db.daily_report.createIndex({ 'metadata.tool_used': 1 });
db.daily_report.createIndex({ 'metadata.agent_type': 1 });

// Insert a sample document to verify the collection works
db.daily_report.insertOne({
  user_input: 'Initialize database',
  response: [
    {
      role: 'assistant',
      content: 'MongoDB initialized successfully with new schema'
    }
  ],
  conversation: {
    Date: new Date().toISOString().split('T')[0],
    Completed: 'Database initialization',
    Inprogress: 'Setting up collections and indexes',
    Blocker: 'None'
  },
  timestamp: new Date(),
  metadata: {
    tool_used: 'save_chat_history_DB',
    source: 'system_init',
    agent_type: 'system',
    version: '2.0.0'
  }
});

print('✅ MongoDB initialization completed successfully');
print('📦 Database: agent_reports (or report based on config)');
print('📋 Collection: daily_report');
print('🔍 Indexes created for timestamp, tool_used, and agent_type');
