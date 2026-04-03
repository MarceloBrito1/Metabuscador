import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchBar from '../../src/components/SearchBar.vue'

describe('SearchBar', () => {
  it('renders an input and a button', () => {
    const wrapper = mount(SearchBar)
    expect(wrapper.find('input[type="search"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('emits search event with the trimmed query on submit', async () => {
    const wrapper = mount(SearchBar)
    const input = wrapper.find('input')
    await input.setValue('  python  ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')[0]).toEqual(['python'])
  })

  it('does not emit search event when input is blank', async () => {
    const wrapper = mount(SearchBar)
    await wrapper.find('input').setValue('   ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('search')).toBeFalsy()
  })

  it('disables input and button while loading', () => {
    const wrapper = mount(SearchBar, { props: { loading: true } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('disables button when input is empty', () => {
    const wrapper = mount(SearchBar)
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('enables button once input has text', async () => {
    const wrapper = mount(SearchBar)
    await wrapper.find('input').setValue('vue')
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('shows spinner when loading', () => {
    const wrapper = mount(SearchBar, { props: { loading: true } })
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })
})
