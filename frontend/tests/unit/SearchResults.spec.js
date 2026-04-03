import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchResults from '../../src/components/SearchResults.vue'

const sampleResults = [
  {
    title: 'Python programming',
    url: 'https://python.org',
    snippet: 'Python is a programming language.',
    source: 'DuckDuckGo',
  },
  {
    title: 'Python (Wikipedia)',
    url: 'https://en.wikipedia.org/wiki/Python',
    snippet: 'Python is interpreted and high-level.',
    source: 'Wikipedia',
  },
]

describe('SearchResults', () => {
  it('shows nothing before a search is done', () => {
    const wrapper = mount(SearchResults, {
      props: { results: [], loading: false, searched: false, query: '' },
    })
    expect(wrapper.text()).toBe('')
  })

  it('shows a loading spinner while loading', () => {
    const wrapper = mount(SearchResults, {
      props: { results: [], loading: true, searched: true, query: 'python' },
    })
    expect(wrapper.find('.spinner-lg').exists()).toBe(true)
    expect(wrapper.text()).toContain('Buscando')
  })

  it('shows empty-state message when searched but no results', () => {
    const wrapper = mount(SearchResults, {
      props: { results: [], loading: false, searched: true, query: 'xyzzy123' },
    })
    expect(wrapper.text()).toContain('Nenhum resultado')
    expect(wrapper.text()).toContain('xyzzy123')
  })

  it('renders a result card for each result', () => {
    const wrapper = mount(SearchResults, {
      props: { results: sampleResults, loading: false, searched: true, query: 'python' },
    })
    const cards = wrapper.findAll('article')
    expect(cards.length).toBe(2)
  })

  it('displays the result count', () => {
    const wrapper = mount(SearchResults, {
      props: { results: sampleResults, loading: false, searched: true, query: 'python' },
    })
    expect(wrapper.text()).toContain('2 resultado(s)')
  })

  it('shows result titles and snippets', () => {
    const wrapper = mount(SearchResults, {
      props: { results: sampleResults, loading: false, searched: true, query: 'python' },
    })
    expect(wrapper.text()).toContain('Python programming')
    expect(wrapper.text()).toContain('Python (Wikipedia)')
    expect(wrapper.text()).toContain('Python is a programming language.')
  })
})
