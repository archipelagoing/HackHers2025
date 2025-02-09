import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import HomeView from '../../views/HomeView.vue';
import { createRouter, createWebHistory } from 'vue-router';
import { routes } from '../../router';  // Import your routes

describe('HomeView', () => {
  it('displays user data when authenticated', async () => {
    // Create a router instance
    const router = createRouter({
      history: createWebHistory(),
      routes
    });

    const wrapper = mount(HomeView, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              auth: {
                user: {
                  username: 'Test User',
                  top_artists: ['Artist 1'],
                  top_genres: ['Pop']
                }
              }
            }
          }),
          router  // Add router to plugins
        ],
        stubs: {
          'router-link': true  // Stub router-link component
        }
      }
    });

    // Wait for component to update
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Welcome Test User');
    expect(wrapper.text()).toContain('Artist 1');
    expect(wrapper.text()).toContain('Pop');
  });
}); 