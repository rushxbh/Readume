"use client"
import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hi! I can help you create a personalized learning roadmap. Would you like to upload your resume?' }
  ]);
  const [userInput, setUserInput] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Add new state for storing resume skills
  const [resumeSkills, setResumeSkills] = useState(null);
  
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setResumeFile(file);
      setMessages(prev => [...prev, 
        { type: 'user', text: 'Resume uploaded: ' + file.name },
        { type: 'bot', text: 'Analyzing your resume...' }
      ]);
      
      const formData = new FormData();
      formData.append('resume', file);
      
      try {
        setLoading(true);
        const response = await fetch('/api/analyze-resume', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        setResumeSkills(data.skills); // Store skills for context

        // Pass skills to Gemini API for recommendations
        const geminiResponse = await fetch('http://localhost:5000/api/gemini-recommendations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ skills: data.skills }),
        });

        if (!geminiResponse.ok) {
          throw new Error('Failed to get recommendations');
        }

        const geminiData = await geminiResponse.json();
        const recommendationsMessage = `Here are some personalized recommendations based on your skills:\n\n${geminiData.recommendations.join('\n')}`;
        setMessages(prev => [...prev, { type: 'bot', text: recommendationsMessage }]);
      } catch (error) {
        setMessages(prev => [...prev, { type: 'bot', text: 'Sorry, there was an error analyzing your resume or fetching recommendations.' }]);
      } finally {
        setLoading(false);
      }
    } else {
      setMessages(prev => [...prev, { type: 'bot', text: 'Please upload a PDF file.' }]);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const userMessage = userInput.trim();
    setUserInput('');
    
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setLoading(true);

    try {
      // Get chat history excluding system messages
      const chatHistory = messages
        .filter(msg => msg.text !== 'Analyzing your resume...')
        .map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.text
        }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          resumeSkills,
          chatHistory
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { type: 'bot', text: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', text: 'Sorry, I encountered an error.' }]);
    } finally {
      setLoading(false);
    }
  };

  // Remove the generateBotResponse function as it's no longer needed
  
  const generateRoadmap = (skills) => {
    // This is a simple roadmap generation - you can make it more sophisticated
    return `Based on your skills, here's a recommended learning path:
    
1. Current Skills: ${skills.join(', ')}

2. Recommended Next Steps:
   - Advanced topics in ${skills[0] || 'your field'}
   - Learn complementary technologies
   - Work on practical projects
   
3. Career Path Options:
   - Continue specializing in your current stack
   - Explore full-stack development
   - Consider cloud certifications

Would you like more specific recommendations for any of these areas?`;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-96 bg-white rounded-lg shadow-xl border">
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
            <h3 className="font-medium">Career Assistant</h3>
            <button onClick={() => setIsOpen(false)} className="text-white hover:text-gray-200">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3/4 p-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.type === 'user' ? (
                    <p className="whitespace-pre-wrap">{message.text}</p>
                  ) : (
                    <ReactMarkdown
                    //   className="prose prose-sm max-w-none"
                      components={{
                        p: ({node, ...props}) => <p className="mb-2" {...props} />,
                        ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                        li: ({node, ...props}) => <li className="mb-1" {...props} />,
                        code: ({node, inline, ...props}) => (
                          inline ? (
                            <code className="bg-gray-200 px-1 rounded" {...props} />
                          ) : (
                            <code className="block bg-gray-200 p-2 rounded my-2 overflow-x-auto" {...props} />
                          )
                        )
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>

          {/* Chat Input Section */}
          <div className="p-4 border-t">
            {!resumeFile ? (
              // Resume upload button when no resume is uploaded
              <div>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf"
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Processing...' : 'Upload Resume (PDF)'}
                </button>
              </div>
            ) : (
              // Chat input form when resume is uploaded
              <form onSubmit={handleSendMessage} className="flex gap-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Send
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}