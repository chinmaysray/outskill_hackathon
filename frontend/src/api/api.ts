// src/lib/api.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiService = {
  async streamAnalysis(request: any, onEvent: (event: any) => void) {
    // Convert request to FormData
    const formData = new FormData();
    formData.append('image', request.image);
    formData.append('user_preferences', JSON.stringify(request.user_preferences || {}));
    if (request.brand_guidelines) {
      formData.append('brand_guidelines', JSON.stringify(request.brand_guidelines));
    }

    const response = await fetch(`${BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.body) throw new Error('No response body for streaming');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let eventType = null;
    let eventData = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventType = line.replace('event:', '').trim();
        } else if (line.startsWith('data:')) {
          eventData += line.replace('data:', '').trim();
        } else if (line.trim() === '') {
          // End of event
          if (eventType && eventData) {
            try {
              const parsedData = JSON.parse(eventData);
              onEvent({ event_type: eventType, data: parsedData });
            } catch (e) {
              // Ignore malformed data
            }
          }
          eventType = null;
          eventData = '';
        }
      }
    }
  },
};