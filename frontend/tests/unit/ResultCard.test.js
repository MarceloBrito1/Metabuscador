import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResultCard from '../../src/components/ResultCard.vue'

const mockResult = {
  title: 'Test Title',
  url: 'https://example.com',
  snippet: 'Test snippet text',
  source: 'DuckDuckGo',
}

describe('ResultCard', () => {
  it('renders title as link', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    const link = wrapper.find('a')
    expect(link.text()).toBe('Test Title')
    expect(link.attributes('href')).toBe('https://example.com')
  })

  it('renders snippet', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.find('.snippet').text()).toBe('Test snippet text')
  })

  it('renders source badge', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.find('.source').text()).toBe('DuckDuckGo')
  })

  it('link opens in new tab', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    const link = wrapper.find('a')
    expect(link.attributes('target')).toBe('_blank')
    expect(link.attributes('rel')).toContain('noopener')
  })
})
