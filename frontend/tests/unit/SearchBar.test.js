import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchBar from '../../src/components/SearchBar.vue'

describe('SearchBar', () => {
  it('renders input and button', () => {
    const wrapper = mount(SearchBar)
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('emits search event with trimmed query', async () => {
    const wrapper = mount(SearchBar)
    await wrapper.find('input').setValue('  python  ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')[0]).toEqual(['python'])
  })

  it('does not emit search for empty query', async () => {
    const wrapper = mount(SearchBar)
    await wrapper.find('input').setValue('   ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('search')).toBeFalsy()
  })

  it('reflects initialQuery prop', () => {
    const wrapper = mount(SearchBar, { props: { initialQuery: 'vue' } })
    expect(wrapper.find('input').element.value).toBe('vue')
  })
})
