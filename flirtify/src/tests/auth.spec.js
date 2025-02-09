import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { useAuthStore } from '../stores/auth';
import { createPinia, setActivePinia } from 'pinia';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { api } from '../services/api';

// Mock API responses
const server = setupServer(
  // Mock Spotify login endpoint
  http.get('http://localhost:8000/auth/login', () => {
    return HttpResponse.json({
      auth_url: 'https://accounts.spotify.com/authorize?some_params'
    })
  }),

  // Mock callback endpoint
  rest.get('http://localhost:8000/auth/callback', (req, res, ctx) => {
    const code = req.url.searchParams.get('code');
    if (code === 'valid_code') {
      return res(
        ctx.json({
          spotify_id: 'test_user_123',
          access_token: 'valid_token_123',
          username: 'Test User'
        })
      );
    }
    return res(ctx.status(400), ctx.json({ error: 'Invalid code' }));
  }),

  // Mock user profile endpoint
  rest.get('http://localhost:8000/users/:userId', (req, res, ctx) => {
    return res(
      ctx.json({
        username: 'Test User',
        top_artists: ['Artist 1', 'Artist 2'],
        top_genres: ['Pop', 'Rock']
      })
    );
  })
);

describe('Authentication Flow', () => {
  beforeAll(() => server.listen());
  afterAll(() => server.close());
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('handles successful login flow', async () => {
    const store = useAuthStore();
    
    // Test initial state
    expect(store.isAuthenticated()).toBe(false);
    
    // Test login URL fetch
    const authUrl = await api.spotifyLogin();
    expect(authUrl).toContain('accounts.spotify.com/authorize');
    
    // Test callback handling
    const userData = await api.handleCallback('valid_code');
    store.setUser(userData);
    
    // Verify authentication state
    expect(store.isAuthenticated()).toBe(true);
    expect(store.user.value.spotify_id).toBe('test_user_123');
    expect(localStorage.getItem('access_token')).toBe('valid_token_123');
  });

  it('handles failed login attempts', async () => {
    const store = useAuthStore();
    
    try {
      await api.handleCallback('invalid_code');
      // Should not reach here
      expect(true).toBe(false);
    } catch (error) {
      expect(error.response.status).toBe(400);
      expect(store.isAuthenticated()).toBe(false);
    }
  });

  it('handles user profile fetch', async () => {
    const store = useAuthStore();
    
    // Setup authenticated state
    store.setUser({
      spotify_id: 'test_user_123',
      access_token: 'valid_token_123'
    });
    
    // Test profile fetch
    const profile = await api.getUserProfile('test_user_123');
    expect(profile.username).toBe('Test User');
    expect(profile.top_artists).toHaveLength(2);
  });

  it('handles token expiration', async () => {
    const store = useAuthStore();
    
    // Mock expired token response
    server.use(
      rest.get('http://localhost:8000/users/:userId', (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json({ error: 'Token expired' })
        );
      })
    );
    
    try {
      await api.getUserProfile('test_user_123');
    } catch (error) {
      expect(error.response.status).toBe(401);
      expect(store.isAuthenticated()).toBe(false);
      expect(localStorage.getItem('access_token')).toBeNull();
    }
  });
}); 