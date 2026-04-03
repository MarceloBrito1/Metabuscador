import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResultCard from '../../src/components/ResultCard.vue'

const mockResult = {
  title: 'Python programming language',
  url: 'https://python.org',
  snippet: 'Python is a high-level language.',
  source: 'DuckDuckGo',
}

describe('ResultCard', () => {
  it('renders the result title as a link', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    const link = wrapper.find('a')
    expect(link.text()).toBe(mockResult.title)
    expect(link.attributes('href')).toBe(mockResult.url)
  })

  it('opens link in a new tab with noopener', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    const link = wrapper.find('a')
    expect(link.attributes('target')).toBe('_blank')
    expect(link.attributes('rel')).toContain('noopener')
  })

  it('renders the snippet text', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.text()).toContain(mockResult.snippet)
  })

  it('renders the source badge', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.find('.badge').text()).toBe('DuckDuckGo')
  })

  it('applies the DuckDuckGo badge class', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.find('.badge').classes()).toContain('badge--ddg')
  })

  it('applies the Wikipedia badge class', () => {
    const wikiResult = { ...mockResult, source: 'Wikipedia' }
    const wrapper = mount(ResultCard, { props: { result: wikiResult } })
    expect(wrapper.find('.badge').classes()).toContain('badge--wiki')
  })

  it('applies default badge class for unknown source', () => {
    const unknownResult = { ...mockResult, source: 'Unknown Engine' }
    const wrapper = mount(ResultCard, { props: { result: unknownResult } })
    expect(wrapper.find('.badge').classes()).toContain('badge--default')
  })

  it('displays the URL', () => {
    const wrapper = mount(ResultCard, { props: { result: mockResult } })
    expect(wrapper.text()).toContain(mockResult.url)
  })
})
