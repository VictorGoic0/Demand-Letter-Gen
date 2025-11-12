# Demand Letter Generator - PR Implementation List
# Part 6: Rich Text Editor Enhancement (Post-MVP)

## Overview
This enhancement replaces the basic textarea editor with Tiptap rich text editor while keeping HTML as the source of truth in the database. The flow is:
- **Fetch:** HTML from DB → Parse to Tiptap → Display in editor
- **Edit:** User edits in Tiptap (Word-like experience)
- **Save:** Tiptap → Convert to HTML → Save to DB
- **Export:** HTML from DB → python-docx → DOCX file

---

## PR #30: Tiptap Installation and Basic Setup

### Package Installation
- [ ] 1. Install @tiptap/react
- [ ] 2. Install @tiptap/starter-kit
- [ ] 3. Install @tiptap/pm (ProseMirror core)
- [ ] 4. Verify dependencies in package.json
- [ ] 5. Test that packages install without conflicts

### Basic Editor Component
- [ ] 6. Create src/components/RichTextEditor/TiptapEditor.tsx
- [ ] 7. Import useEditor hook from @tiptap/react
- [ ] 8. Import EditorContent component from @tiptap/react
- [ ] 9. Import StarterKit extension
- [ ] 10. Create basic editor configuration:
  - [ ] Initialize with StarterKit extension
  - [ ] Set editable to true
  - [ ] Configure empty content initially
- [ ] 11. Return EditorContent component wrapped in container div
- [ ] 12. Add TypeScript types for editor props
- [ ] 13. Test basic editor renders

### Code Splitting Setup
- [ ] 14. Create src/components/RichTextEditor/index.ts as lazy-load wrapper
- [ ] 15. Export TiptapEditor as lazy-loaded component:
  - [ ] Use React.lazy() to import TiptapEditor
  - [ ] Export with displayName for debugging
- [ ] 16. Create loading fallback component (simple spinner)
- [ ] 17. Test that lazy loading works in development
- [ ] 18. Verify bundle analyzer shows Tiptap in separate chunk

### Editor Styling
- [ ] 19. Create src/components/RichTextEditor/editor-styles.css
- [ ] 20. Style editor container:
  - [ ] Border
  - [ ] Padding
  - [ ] Min-height
  - [ ] Background color
- [ ] 21. Style editor content (.ProseMirror class):
  - [ ] Typography (font-family, size, line-height)
  - [ ] Paragraph spacing
  - [ ] Focus outline
- [ ] 22. Style headings (h1, h2, h3):
  - [ ] Font sizes
  - [ ] Font weights
  - [ ] Margins
- [ ] 23. Style lists (ul, ol):
  - [ ] Proper indentation
  - [ ] List markers
  - [ ] Nested list spacing
- [ ] 24. Style bold/italic text
- [ ] 25. Add focus styles for better UX
- [ ] 26. Make responsive for mobile devices
- [ ] 27. Import styles in TiptapEditor component

---

## PR #31: HTML Content Integration

### HTML Loading
- [ ] 1. Update TiptapEditor.tsx to accept initialContent prop
- [ ] 2. Add initialContent to useEditor configuration:
  - [ ] Pass as content field
  - [ ] Type as string (HTML)
- [ ] 3. Test loading simple HTML: `<h1>Test</h1><p>Content</p>`
- [ ] 4. Test loading complex HTML with formatting:
  - [ ] Headings (h1, h2, h3)
  - [ ] Bold and italic text
  - [ ] Lists (ul, ol)
  - [ ] Multiple paragraphs
- [ ] 5. Verify HTML entities are properly decoded
- [ ] 6. Test loading empty content
- [ ] 7. Test loading malformed HTML (error handling)

### HTML Export
- [ ] 8. Add getHTML method to editor instance
- [ ] 9. Create onChange handler prop for TiptapEditor
- [ ] 10. Add onUpdate callback to useEditor config:
  - [ ] Extract HTML using editor.getHTML()
  - [ ] Call onChange with HTML string
- [ ] 11. Add debouncing to onChange (prevent too many updates):
  - [ ] Use lodash debounce or custom hook
  - [ ] Set 500ms delay
- [ ] 12. Test HTML export matches input format
- [ ] 13. Test HTML export preserves formatting:
  - [ ] Headings maintain h1, h2, h3 tags
  - [ ] Bold/italic maintain <strong>, <em> tags
  - [ ] Lists maintain <ul>, <ol>, <li> structure
- [ ] 14. Test exported HTML can be re-imported correctly

### Content Validation
- [ ] 15. Add HTML sanitization on import (prevent XSS):
  - [ ] Use DOMPurify library
  - [ ] Whitelist safe tags
  - [ ] Remove script tags and event handlers
- [ ] 16. Add content length validation
- [ ] 17. Handle edge cases:
  - [ ] Very large content (>100KB)
  - [ ] Special characters
  - [ ] Unicode content
- [ ] 18. Add error boundaries for parsing failures

---

## PR #32: Editor Toolbar

### Toolbar Component
- [ ] 1. Create src/components/RichTextEditor/Toolbar.tsx
- [ ] 2. Accept editor instance as prop
- [ ] 3. Create toolbar container with proper styling
- [ ] 4. Add sticky positioning (stays visible on scroll)

### Text Formatting Buttons
- [ ] 5. Add Bold button:
  - [ ] Icon from lucide-react
  - [ ] onClick: editor.chain().focus().toggleBold().run()
  - [ ] Active state when text is bold
  - [ ] Keyboard shortcut tooltip (Cmd+B)
- [ ] 6. Add Italic button:
  - [ ] Icon from lucide-react
  - [ ] onClick: editor.chain().focus().toggleItalic().run()
  - [ ] Active state when text is italic
  - [ ] Keyboard shortcut tooltip (Cmd+I)
- [ ] 7. Add Underline button (if needed):
  - [ ] Requires @tiptap/extension-underline
  - [ ] Same pattern as bold/italic
- [ ] 8. Add Strikethrough button:
  - [ ] editor.chain().focus().toggleStrike().run()
  - [ ] Active state

### Heading Buttons
- [ ] 9. Add Heading 1 button:
  - [ ] editor.chain().focus().toggleHeading({ level: 1 }).run()
  - [ ] Active when current block is h1
- [ ] 10. Add Heading 2 button:
  - [ ] Same pattern for level 2
- [ ] 11. Add Heading 3 button:
  - [ ] Same pattern for level 3
- [ ] 12. Add "Normal Text" button:
  - [ ] editor.chain().focus().setParagraph().run()
  - [ ] Active when current block is paragraph
- [ ] 13. Consider dropdown for heading selection instead of individual buttons

### List Buttons
- [ ] 14. Add Bullet List button:
  - [ ] editor.chain().focus().toggleBulletList().run()
  - [ ] Active when in bullet list
- [ ] 15. Add Numbered List button:
  - [ ] editor.chain().focus().toggleOrderedList().run()
  - [ ] Active when in ordered list

### Additional Formatting
- [ ] 16. Add Blockquote button (optional):
  - [ ] editor.chain().focus().toggleBlockquote().run()
- [ ] 17. Add Horizontal Rule button (optional):
  - [ ] editor.chain().focus().setHorizontalRule().run()

### Toolbar Styling
- [ ] 18. Style toolbar buttons:
  - [ ] Hover states
  - [ ] Active states (blue background or similar)
  - [ ] Disabled states
  - [ ] Icon sizing
- [ ] 19. Add button groups with separators
- [ ] 20. Make toolbar responsive:
  - [ ] Wrap on mobile
  - [ ] Or horizontal scroll
  - [ ] Or collapsed menu
- [ ] 21. Add tooltips to all buttons
- [ ] 22. Test keyboard shortcuts work

---

## PR #33: Integration with Letter Pages

### Update LetterEditor Component
- [ ] 1. Open src/components/Letters/LetterEditor.tsx
- [ ] 2. Import lazy and Suspense from React
- [ ] 3. Import lazy-loaded TiptapEditor from RichTextEditor/index
- [ ] 4. Wrap TiptapEditor in Suspense component with loading fallback
- [ ] 5. Remove existing textarea implementation
- [ ] 6. Import Toolbar component
- [ ] 7. Pass initialContent (HTML from props) to TiptapEditor
- [ ] 8. Set up onChange handler:
  - [ ] Receive HTML from TiptapEditor
  - [ ] Call parent onChange callback
  - [ ] Update local state if needed
- [ ] 9. Render Toolbar above TiptapEditor
- [ ] 10. Render TiptapEditor with proper styling
- [ ] 11. Test that existing LetterEditor props still work
- [ ] 12. Test that lazy loading works (check Network tab)
- [ ] 13. Verify loading fallback appears briefly
- [ ] 14. Remove old textarea-related code

### Update Finalize Letter Page
- [ ] 15. Open src/pages/FinalizeLetter.tsx
- [ ] 16. Verify LetterEditor receives HTML content correctly
- [ ] 17. Test view mode → edit mode transition
- [ ] 18. Test editing content in Tiptap editor
- [ ] 19. Test save functionality:
  - [ ] Tiptap → HTML conversion
  - [ ] HTML saved to database
  - [ ] Content persists after save
- [ ] 20. Test switching back to view mode shows updated content
- [ ] 21. Test that formatting is preserved through save cycle

### Update Edit Letter Page
- [ ] 22. Open src/pages/EditLetter.tsx
- [ ] 23. Verify LetterEditor integration works
- [ ] 24. Test loading existing letter content
- [ ] 25. Test editing and saving
- [ ] 26. Test view/edit mode toggling
- [ ] 27. Verify re-export functionality still works

### Testing Full Flow
- [ ] 28. Test AI-generated letter → Tiptap editor:
  - [ ] Generate new letter via AI
  - [ ] Open in finalize page
  - [ ] Verify HTML renders correctly in Tiptap
  - [ ] Verify all formatting preserved
- [ ] 29. Test edit → save → reload cycle:
  - [ ] Make edits in Tiptap
  - [ ] Save changes
  - [ ] Refresh page or navigate away and back
  - [ ] Verify changes persisted
- [ ] 30. Test complex formatting:
  - [ ] Multiple heading levels
  - [ ] Nested lists
  - [ ] Mixed bold/italic text
  - [ ] Long paragraphs
- [ ] 31. Test edge cases:
  - [ ] Empty content
  - [ ] Very long content
  - [ ] Special characters
  - [ ] Content with HTML entities

---

## PR #34: Read-Only Mode for Letter Viewer

### Read-Only Editor
- [ ] 1. Update TiptapEditor to accept editable prop
- [ ] 2. Pass editable to useEditor configuration
- [ ] 3. When editable=false:
  - [ ] Disable all editing
  - [ ] Remove cursor
  - [ ] Prevent text selection for editing (allow for copy)
- [ ] 4. Hide toolbar when in read-only mode
- [ ] 5. Style read-only mode differently:
  - [ ] Remove border or make subtle
  - [ ] Adjust background
  - [ ] Make it look like rendered document

### Update LetterViewer Component
- [ ] 6. Open src/components/Letters/LetterViewer.tsx
- [ ] 7. Replace existing HTML rendering with TiptapEditor
- [ ] 8. Set editable={false}
- [ ] 9. Pass content as initialContent
- [ ] 10. Remove onChange handler (not needed in view mode)
- [ ] 11. Apply proper styling for document view:
  - [ ] Wider line spacing
  - [ ] Professional font
  - [ ] Print-friendly appearance

### Testing View Mode
- [ ] 12. Test LetterViewer shows content correctly
- [ ] 13. Verify no editing is possible
- [ ] 14. Verify toolbar is hidden
- [ ] 15. Test that formatting renders properly
- [ ] 16. Test on Finalize page (view mode)
- [ ] 17. Test on Edit page (view mode)
- [ ] 18. Verify print styles still work

---

## PR #35: Additional Tiptap Extensions (Optional Enhancements)

### Text Alignment
- [ ] 1. Install @tiptap/extension-text-align
- [ ] 2. Add to editor extensions
- [ ] 3. Add toolbar buttons:
  - [ ] Align left
  - [ ] Align center
  - [ ] Align right
  - [ ] Justify
- [ ] 4. Test alignment persists in HTML export

### Text Color & Highlighting
- [ ] 5. Install @tiptap/extension-color
- [ ] 6. Install @tiptap/extension-text-style
- [ ] 7. Install @tiptap/extension-highlight
- [ ] 8. Add color picker to toolbar
- [ ] 9. Add highlight color picker
- [ ] 10. Test colors export to HTML correctly

### Tables (If Needed for Legal Docs)
- [ ] 11. Install @tiptap/extension-table
- [ ] 12. Install @tiptap/extension-table-row
- [ ] 13. Install @tiptap/extension-table-cell
- [ ] 14. Install @tiptap/extension-table-header
- [ ] 15. Add table insertion button to toolbar
- [ ] 16. Add table row/column manipulation buttons
- [ ] 17. Style tables appropriately
- [ ] 18. Test table export to HTML
- [ ] 19. Verify tables convert properly to DOCX

### Link Support
- [ ] 20. Install @tiptap/extension-link
- [ ] 21. Add link button to toolbar
- [ ] 22. Create link dialog/modal:
  - [ ] URL input
  - [ ] Link text input
  - [ ] Insert button
- [ ] 23. Add edit/remove link functionality
- [ ] 24. Test links export correctly

### Character Count
- [ ] 25. Install @tiptap/extension-character-count
- [ ] 26. Add character count display below editor
- [ ] 27. Add word count display
- [ ] 28. Style count display subtly

### Placeholder Text
- [ ] 29. Install @tiptap/extension-placeholder
- [ ] 30. Add placeholder text: "Start typing your demand letter..."
- [ ] 31. Style placeholder appropriately

---

## PR #36: Mobile Optimization for Rich Text Editor

### Touch Interactions
- [ ] 1. Test toolbar buttons on touch devices:
  - [ ] Ensure tap targets are at least 44x44px
  - [ ] Add touch feedback (active states)
- [ ] 2. Test text selection on mobile:
  - [ ] Selection handles appear correctly
  - [ ] Can select and format text
- [ ] 3. Test scrolling behavior:
  - [ ] Editor scrolls smoothly
  - [ ] Toolbar remains accessible

### Mobile Toolbar
- [ ] 4. Create responsive toolbar layout:
  - [ ] Show most important buttons first
  - [ ] Collapse less-used buttons into menu
  - [ ] Or allow horizontal scrolling
- [ ] 5. Add "More" menu for additional formatting options
- [ ] 6. Test toolbar on various screen sizes:
  - [ ] iPhone SE (small)
  - [ ] Standard mobile (375px)
  - [ ] Tablet (768px)

### Keyboard Behavior
- [ ] 7. Test iOS keyboard behavior:
  - [ ] Editor doesn't get hidden by keyboard
  - [ ] Scroll to keep cursor visible
- [ ] 8. Test Android keyboard behavior
- [ ] 9. Add "Done" button to close keyboard
- [ ] 10. Test formatting toolbar appears above keyboard (iOS)

### Performance on Mobile
- [ ] 11. Test with long documents (10+ pages)
- [ ] 12. Optimize rendering performance if needed
- [ ] 13. Test on lower-end devices
- [ ] 14. Monitor memory usage

---

## PR #37: Accessibility Improvements

### Keyboard Navigation
- [ ] 1. Ensure all toolbar buttons are keyboard accessible
- [ ] 2. Test Tab key navigation through toolbar
- [ ] 3. Add keyboard shortcuts documentation
- [ ] 4. Test Escape key behavior (close menus)
- [ ] 5. Ensure editor is keyboard-only navigable

### Screen Reader Support
- [ ] 6. Add ARIA labels to toolbar buttons
- [ ] 7. Add ARIA role="toolbar" to toolbar container
- [ ] 8. Add ARIA live region for editor status
- [ ] 9. Test with VoiceOver (macOS/iOS)
- [ ] 10. Test with NVDA (Windows)
- [ ] 11. Add screen reader announcements for formatting changes

### Visual Accessibility
- [ ] 12. Ensure sufficient color contrast:
  - [ ] Toolbar buttons
  - [ ] Active states
  - [ ] Editor text
- [ ] 13. Add focus indicators for keyboard navigation
- [ ] 14. Test with reduced motion preferences
- [ ] 15. Test with high contrast mode
- [ ] 16. Ensure minimum font size is readable

### Error States
- [ ] 17. Add clear error messages for:
  - [ ] Content too long
  - [ ] Invalid HTML
  - [ ] Save failures
- [ ] 18. Make errors keyboard accessible
- [ ] 19. Announce errors to screen readers

---

## PR #38: Testing and Documentation

### Unit Tests
- [ ] 1. Create tests/components/TiptapEditor.test.tsx
- [ ] 2. Test editor initialization
- [ ] 3. Test HTML loading
- [ ] 4. Test HTML export
- [ ] 5. Test onChange callback
- [ ] 6. Test toolbar button interactions
- [ ] 7. Test formatting commands
- [ ] 8. Test read-only mode

### Integration Tests
- [ ] 9. Test full edit flow:
  - [ ] Load letter
  - [ ] Edit in Tiptap
  - [ ] Save
  - [ ] Reload
  - [ ] Verify changes
- [ ] 10. Test AI generation → Tiptap → Save → Export flow
- [ ] 11. Test multiple formatting operations in sequence

### Documentation
- [ ] 12. Create docs/rich-text-editor.md
- [ ] 13. Document architecture:
  - [ ] HTML as source of truth
  - [ ] Conversion flow diagram
  - [ ] Component hierarchy
- [ ] 14. Document available formatting options
- [ ] 15. Document keyboard shortcuts
- [ ] 16. Document how to add new extensions
- [ ] 17. Add troubleshooting section
- [ ] 18. Update main README with Tiptap info

### User Guide Updates
- [ ] 19. Add screenshots of rich text editor
- [ ] 20. Document formatting toolbar usage
- [ ] 21. Add tips for effective formatting
- [ ] 22. Document keyboard shortcuts for users
- [ ] 23. Add FAQ about rich text editing

---

## PR #39: Performance Optimization

### Bundle Size
- [ ] 1. Install webpack-bundle-analyzer or vite-plugin-bundle-analyzer
- [ ] 2. Analyze bundle size impact of Tiptap
- [ ] 3. Verify Tiptap is in separate chunk (due to lazy loading)
- [ ] 4. Ensure tree-shaking is working
- [ ] 5. Verify lazy loading reduces initial bundle size
- [ ] 6. Test that Tiptap chunk loads only when needed
- [ ] 7. Optimize extension imports (only import what's needed)
- [ ] 8. Document bundle size before/after in PR

### Rendering Performance
- [ ] 9. Profile editor rendering with React DevTools
- [ ] 10. Add memoization where appropriate
- [ ] 11. Test with very long documents (20+ pages):
  - [ ] Measure render time
  - [ ] Optimize if needed
- [ ] 12. Consider virtualization for very long documents (optional)

### Debouncing and Throttling
- [ ] 13. Verify onChange debouncing works well:
  - [ ] Not too fast (too many API calls)
  - [ ] Not too slow (feels laggy)
  - [ ] Test different debounce values
- [ ] 14. Add loading indicator for save operations
- [ ] 15. Implement optimistic updates

### Memory Management
- [ ] 16. Verify editor cleanup on unmount
- [ ] 17. Test for memory leaks with long editing sessions
- [ ] 18. Profile memory usage with Chrome DevTools

---

## Notes

### Estimated Implementation Time
- **PR #30:** 2-3 hours (installation and basic setup)
- **PR #31:** 3-4 hours (HTML integration and testing)
- **PR #32:** 4-5 hours (full toolbar with all buttons)
- **PR #33:** 3-4 hours (integration with existing pages)
- **PR #34:** 2 hours (read-only mode)
- **PR #35:** 4-6 hours (optional extensions, pick what you need)
- **PR #36:** 3-4 hours (mobile optimization)
- **PR #37:** 3-4 hours (accessibility)
- **PR #38:** 4-5 hours (testing and documentation)
- **PR #39:** 2-3 hours (performance optimization)

**Total:** ~30-40 hours (1 week full-time or 2 weeks part-time)

### Dependencies
- Core Tiptap: @tiptap/react, @tiptap/starter-kit (~100KB gzipped)
- Optional extensions add ~10-30KB each
- DOMPurify for sanitization: ~15KB

### Browser Support
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support with testing needed

