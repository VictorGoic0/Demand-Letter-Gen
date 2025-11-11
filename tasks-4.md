# Demand Letter Generator - PR Implementation List
# Part 4: Frontend Pages

## PR #16: Document Library Page - Frontend

### Document API Hooks
- [ ] 1. Create src/hooks/useDocuments.ts
- [ ] 2. Implement useDocuments hook:
  - [ ] Use axios to fetch documents
  - [ ] Handle loading state
  - [ ] Handle error state
  - [ ] Return documents list
- [ ] 3. Implement useDocumentUpload hook:
  - [ ] Accept file and upload progress callback
  - [ ] Use FormData for multipart upload
  - [ ] Handle upload progress
  - [ ] Handle success/error
- [ ] 4. Implement useDocumentDelete hook:
  - [ ] Accept document ID
  - [ ] Call delete endpoint
  - [ ] Handle success/error
- [ ] 5. Implement useDocumentDownload hook:
  - [ ] Fetch presigned URL
  - [ ] Trigger browser download

### Document Components
- [ ] 6. Create src/components/Documents/DocumentUpload.tsx
- [ ] 7. Add drag-and-drop zone:
  - [ ] Handle drag events
  - [ ] Visual feedback for drag over
  - [ ] File input hidden with click to select
- [ ] 8. Add file validation:
  - [ ] Check file type (PDF only)
  - [ ] Check file size (max 50MB)
  - [ ] Show error messages
- [ ] 9. Add upload progress bar
- [ ] 10. Add upload success/error messages
- [ ] 11. Create src/components/Documents/DocumentList.tsx
- [ ] 12. Display documents in table/list format:
  - [ ] Filename column
  - [ ] Upload date column
  - [ ] File size column
  - [ ] Actions column (download, delete)
- [ ] 13. Add sorting functionality:
  - [ ] Sort by filename (asc/desc)
  - [ ] Sort by upload date (asc/desc)
  - [ ] Sort by file size (asc/desc)
- [ ] 14. Add delete confirmation dialog
- [ ] 15. Add download button with loading state
- [ ] 16. Add empty state when no documents
- [ ] 17. Create src/components/Documents/DocumentCard.tsx (alternative list view)
- [ ] 18. Display document metadata in card format
- [ ] 19. Add hover effects and interactions

### Document Library Page
- [ ] 20. Create src/pages/DocumentLibrary.tsx
- [ ] 21. Add page header with title
- [ ] 22. Add "Upload Documents" button
- [ ] 23. Render DocumentUpload component in dialog/modal
- [ ] 24. Render DocumentList component
- [ ] 25. Add loading skeleton while fetching
- [ ] 26. Add error state display
- [ ] 27. Add refresh button
- [ ] 28. Implement pagination if needed
- [ ] 29. Add search/filter functionality (stretch)

---

## PR #17: Template Management Page - Frontend

### Template API Hooks
- [ ] 1. Create src/hooks/useTemplates.ts
- [ ] 2. Implement useTemplates hook:
  - [ ] Fetch templates for firm
  - [ ] Handle loading/error states
  - [ ] Return templates list
- [ ] 3. Implement useDefaultTemplate hook:
  - [ ] Fetch default template
  - [ ] Return template or null
- [ ] 4. Implement useCreateTemplate hook:
  - [ ] Accept template data
  - [ ] Call create endpoint
  - [ ] Handle success/error
- [ ] 5. Implement useUpdateTemplate hook:
  - [ ] Accept template ID and data
  - [ ] Call update endpoint
  - [ ] Handle success/error
- [ ] 6. Implement useDeleteTemplate hook:
  - [ ] Accept template ID
  - [ ] Call delete endpoint
  - [ ] Handle success/error

### Template Form Component
- [ ] 7. Create src/components/Templates/TemplateForm.tsx
- [ ] 8. Add template name input field
- [ ] 9. Add letterhead text textarea
- [ ] 10. Add opening paragraph textarea
- [ ] 11. Add closing paragraph textarea
- [ ] 12. Add sections management:
  - [ ] List of section names
  - [ ] Add section button
  - [ ] Remove section button
  - [ ] Reorder sections (drag-drop or buttons)
- [ ] 13. Add "Set as Default" checkbox
- [ ] 14. Add form validation
- [ ] 15. Add save button with loading state
- [ ] 16. Add cancel button
- [ ] 17. Handle create vs edit mode
- [ ] 18. Pre-fill form in edit mode

### Template Display Components
- [ ] 19. Create src/components/Templates/TemplateCard.tsx
- [ ] 20. Display template name
- [ ] 21. Display "Default" badge if is_default
- [ ] 22. Display section count
- [ ] 23. Display created date
- [ ] 24. Add edit button
- [ ] 25. Add delete button
- [ ] 26. Add delete confirmation dialog
- [ ] 27. Create src/components/Templates/TemplateList.tsx
- [ ] 28. Render grid/list of TemplateCards
- [ ] 29. Add empty state
- [ ] 30. Add loading skeleton

### Template Management Page
- [ ] 31. Create src/pages/TemplateManagement.tsx
- [ ] 32. Add page header with title
- [ ] 33. Add "Create Template" button
- [ ] 34. Show TemplateForm in dialog on create
- [ ] 35. Render TemplateList component
- [ ] 36. Handle edit: open dialog with TemplateForm pre-filled
- [ ] 37. Handle delete with confirmation
- [ ] 38. Add loading state
- [ ] 39. Add error state
- [ ] 40. Refresh list after create/update/delete

---

## PR #18: Create Letter Page - Frontend

### Letter Generation API Hooks
- [ ] 1. Create src/hooks/useLetterGeneration.ts
- [ ] 2. Implement useGenerateLetter hook:
  - [ ] Accept template ID and document IDs
  - [ ] Call generate endpoint
  - [ ] Handle loading state (can take up to 30s)
  - [ ] Handle success/error
  - [ ] Return generated letter data

### Document Selection Component
- [ ] 3. Create src/components/CreateLetter/DocumentSelector.tsx
- [ ] 4. Fetch and display available documents
- [ ] 5. Add checkbox for each document
- [ ] 6. Enforce max selection of 5 documents:
  - [ ] Disable checkboxes when 5 selected
  - [ ] Show message "Maximum 5 documents"
- [ ] 7. Display selected count (e.g., "3 of 5 selected")
- [ ] 8. Add search/filter for documents
- [ ] 9. Show document metadata (name, date, size)
- [ ] 10. Add "Clear Selection" button

### Template Selection Component
- [ ] 11. Create src/components/CreateLetter/TemplateSelector.tsx
- [ ] 12. Fetch and display available templates
- [ ] 13. Render as dropdown/select or radio buttons
- [ ] 14. Pre-select default template if exists
- [ ] 15. Show template preview on selection (optional)
- [ ] 16. Handle case where no templates exist

### Generation Progress Component
- [ ] 17. Create src/components/CreateLetter/GenerationProgress.tsx
- [ ] 18. Show loading spinner during generation
- [ ] 19. Show progress message "Generating your demand letter..."
- [ ] 20. Show estimated time remaining (optional)
- [ ] 21. Add cancel button (optional, if API supports)

### Create Letter Page
- [ ] 22. Create src/pages/CreateLetter.tsx
- [ ] 23. Add page header with title and description
- [ ] 24. Add optional title input for letter
- [ ] 25. Render TemplateSelector component
- [ ] 26. Render DocumentSelector component
- [ ] 27. Add "Generate Letter" button:
  - [ ] Disabled if template or documents not selected
  - [ ] Disabled if < 1 or > 5 documents selected
- [ ] 28. Show GenerationProgress when generating
- [ ] 29. On success, redirect to /letters/:id/finalize
- [ ] 30. On error, show error message with retry option
- [ ] 31. Add form validation and error states
- [ ] 32. Add helpful messages/tooltips

---

## PR #19: Finalize Letter Page - Frontend

### Letter Display Component
- [ ] 1. Create src/components/Letters/LetterViewer.tsx
- [ ] 2. Accept content prop (HTML string)
- [ ] 3. Render HTML content safely using react-markdown or dangerouslySetInnerHTML with sanitization
- [ ] 4. Apply proper styling to rendered HTML
- [ ] 5. Add formatting for:
  - [ ] Headings
  - [ ] Paragraphs
  - [ ] Bold/italic text
  - [ ] Lists
- [ ] 6. Make scrollable if content is long
- [ ] 7. Add print-friendly styles

### Letter Editor Component
- [ ] 8. Create src/components/Letters/LetterEditor.tsx
- [ ] 9. Accept content prop and onChange callback
- [ ] 10. Use rich text editor or large textarea
- [ ] 11. Preserve HTML formatting in edit mode
- [ ] 12. Add basic formatting toolbar (optional):
  - [ ] Bold, italic
  - [ ] Headings
  - [ ] Lists
- [ ] 13. Add character/word count (optional)
- [ ] 14. Auto-save draft functionality (optional)

### Finalize Letter API Hooks
- [ ] 15. Create src/hooks/useLetterFinalize.ts
- [ ] 16. Implement useUpdateLetter hook:
  - [ ] Accept letter ID and updated content
  - [ ] Call update endpoint
  - [ ] Handle success/error
- [ ] 17. Implement useFinalizeLetter hook:
  - [ ] Accept letter ID
  - [ ] Call finalize endpoint
  - [ ] Handle loading (docx generation)
  - [ ] Handle success/error
  - [ ] Return download URL

### Finalize Letter Page
- [ ] 18. Create src/pages/FinalizeLetter.tsx
- [ ] 19. Fetch letter by ID from URL params
- [ ] 20. Add page header with letter title
- [ ] 21. Add "Edit" button (top right)
- [ ] 22. Add "Save" button (top right, visible in edit mode)
- [ ] 23. Add "Finalize" button (bottom right)
- [ ] 24. Implement view mode:
  - [ ] Show LetterViewer component
  - [ ] "Edit" button visible
- [ ] 25. Implement edit mode:
  - [ ] Show LetterEditor component
  - [ ] "Save" button visible
  - [ ] "Edit" button hidden
- [ ] 26. Handle save action:
  - [ ] Call useUpdateLetter hook
  - [ ] Show success message
  - [ ] Switch back to view mode
  - [ ] Handle errors
- [ ] 27. Handle finalize action:
  - [ ] Show confirmation dialog
  - [ ] Call useFinalizeLetter hook
  - [ ] Show loading state during docx generation
  - [ ] On success, redirect to /letters
  - [ ] Show success message with download link
  - [ ] Handle errors
- [ ] 28. Add loading state while fetching letter
- [ ] 29. Handle case where letter doesn't exist
- [ ] 30. Handle case where letter is already finalized (redirect to edit page)

---

## PR #20: Generated Letters Library Page - Frontend

### Letter List API Hooks
- [ ] 1. Create src/hooks/useLetters.ts
- [ ] 2. Implement useLetters hook:
  - [ ] Fetch letters list
  - [ ] Accept sorting params
  - [ ] Accept filter params (status)
  - [ ] Handle pagination
  - [ ] Handle loading/error
- [ ] 3. Implement useDeleteLetter hook:
  - [ ] Accept letter ID
  - [ ] Call delete endpoint
  - [ ] Handle success/error
- [ ] 4. Implement useExportLetter hook:
  - [ ] Accept letter ID
  - [ ] Call export endpoint
  - [ ] Return download URL
  - [ ] Handle errors

### Letter Card Component
- [ ] 5. Create src/components/Letters/LetterCard.tsx
- [ ] 6. Display letter title
- [ ] 7. Display status badge:
  - [ ] "Draft" badge for draft status
  - [ ] No badge for created status
- [ ] 8. Display created date
- [ ] 9. Display last modified date
- [ ] 10. Display template name (if available)
- [ ] 11. Add "Edit" button
- [ ] 12. Add "Download" button (if finalized)
- [ ] 13. Add "Delete" button with confirmation
- [ ] 14. Add click handler to open edit page
- [ ] 15. Add hover effects

### Letter List Component
- [ ] 16. Create src/components/Letters/LetterList.tsx
- [ ] 17. Render grid or list of LetterCards
- [ ] 18. Add sorting controls:
  - [ ] Sort by date created
  - [ ] Sort by date modified
  - [ ] Sort by title
  - [ ] Sort by status
- [ ] 19. Add filter controls:
  - [ ] Filter by status (all, draft, created)
- [ ] 20. Add search functionality
- [ ] 21. Add empty state when no letters
- [ ] 22. Add loading skeleton
- [ ] 23. Implement pagination if needed

### Generated Letters Page
- [ ] 24. Create src/pages/GeneratedLetters.tsx
- [ ] 25. Add page header with title
- [ ] 26. Add "Create New Letter" button (links to /create-letter)
- [ ] 27. Render sorting and filter controls
- [ ] 28. Render LetterList component
- [ ] 29. Handle edit: navigate to /letters/:id/edit
- [ ] 30. Handle download: trigger file download
- [ ] 31. Handle delete with confirmation dialog
- [ ] 32. Add loading state
- [ ] 33. Add error state
- [ ] 34. Refresh list after delete

---

## PR #21: Edit Letter Page - Frontend

### Edit Letter Page
- [ ] 1. Create src/pages/EditLetter.tsx
- [ ] 2. Fetch letter by ID from URL params
- [ ] 3. Verify letter exists
- [ ] 4. Add page header with letter title
- [ ] 5. Add back button to return to letters library
- [ ] 6. Add "Edit" button (top right)
- [ ] 7. Add "Save" button (top right, visible in edit mode)
- [ ] 8. Add "Re-export" button (if letter is finalized)
- [ ] 9. Add "Download" button (if docx exists)
- [ ] 10. Implement view mode:
  - [ ] Show LetterViewer component (reuse from PR #19)
  - [ ] "Edit" button visible
  - [ ] Download button visible if docx exists
- [ ] 11. Implement edit mode:
  - [ ] Show LetterEditor component (reuse from PR #19)
  - [ ] "Save" button visible
  - [ ] "Edit" button hidden
- [ ] 12. Handle save action:
  - [ ] Call useUpdateLetter hook
  - [ ] Show success message
  - [ ] Switch back to view mode
  - [ ] Update letter data
  - [ ] Handle errors
- [ ] 13. Handle re-export action:
  - [ ] Show confirmation dialog
  - [ ] Call useExportLetter hook
  - [ ] Show loading state
  - [ ] On success, update download URL
  - [ ] Show success message
  - [ ] Handle errors
- [ ] 14. Handle download action:
  - [ ] Trigger browser download using download URL
- [ ] 15. Add loading state while fetching letter
- [ ] 16. Handle case where letter doesn't exist (404)
- [ ] 17. Add unsaved changes warning when navigating away from edit mode
- [ ] 18. Handle draft letters:
  - [ ] Show "Finalize" button instead of "Re-export"
  - [ ] On finalize, redirect to finalize page or show finalize flow

