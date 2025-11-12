# Demand Letter Generator - PR Implementation List
# Part 4: Frontend Pages

## PR #16: Document Library Page - Frontend

### Document API Hooks
- [x] 1. Create src/hooks/useDocuments.ts
- [x] 2. Implement useDocuments hook:
  - [x] Use axios to fetch documents
  - [x] Handle loading state
  - [x] Handle error state
  - [x] Return documents list
- [x] 3. Implement useDocumentUpload hook:
  - [x] Accept file and upload progress callback
  - [x] Use FormData for multipart upload
  - [x] Handle upload progress
  - [x] Handle success/error
- [x] 4. Implement useDocumentDelete hook:
  - [x] Accept document ID
  - [x] Call delete endpoint
  - [x] Handle success/error
- [x] 5. Implement useDocumentDownload hook:
  - [x] Fetch presigned URL
  - [x] Trigger browser download

### Document Components
- [x] 6. Create src/components/Documents/DocumentUpload.tsx
- [x] 7. Add drag-and-drop zone:
  - [x] Handle drag events
  - [x] Visual feedback for drag over
  - [x] File input hidden with click to select
- [x] 8. Add file validation:
  - [x] Check file type (PDF only)
  - [x] Check file size (max 50MB)
  - [x] Show error messages
- [x] 9. Add upload progress bar
- [x] 10. Add upload success/error messages
- [x] 11. Create src/components/Documents/DocumentList.tsx
- [x] 12. Display documents in table/list format:
  - [x] Filename column
  - [x] Upload date column
  - [x] File size column
  - [x] Actions column (download, delete)
- [x] 13. Add sorting functionality:
  - [x] Sort by filename (asc/desc)
  - [x] Sort by upload date (asc/desc)
  - [x] Sort by file size (asc/desc)
- [x] 14. Add delete confirmation dialog
- [x] 15. Add download button with loading state
- [x] 16. Add empty state when no documents
- [x] 17. Create src/components/Documents/DocumentCard.tsx (alternative list view)
- [x] 18. Display document metadata in card format
- [x] 19. Add hover effects and interactions

### Document Library Page
- [x] 20. Create src/pages/DocumentLibrary.tsx
- [x] 21. Add page header with title
- [x] 22. Add "Upload Documents" button
- [x] 23. Render DocumentUpload component in dialog/modal
- [x] 24. Render DocumentList component
- [x] 25. Add loading skeleton while fetching
- [x] 26. Add error state display
- [x] 27. Add refresh button
- [x] 28. Implement pagination if needed
- [x] 29. Add search/filter functionality (stretch)

---

## PR #17: Template Management Page - Frontend

### Template API Hooks
- [x] 1. Create src/hooks/useTemplates.ts
- [x] 2. Implement useTemplates hook:
  - [x] Fetch templates for firm
  - [x] Handle loading/error states
  - [x] Return templates list
- [x] 3. Implement useDefaultTemplate hook:
  - [x] Fetch default template
  - [x] Return template or null
- [x] 4. Implement useCreateTemplate hook:
  - [x] Accept template data
  - [x] Call create endpoint
  - [x] Handle success/error
- [x] 5. Implement useUpdateTemplate hook:
  - [x] Accept template ID and data
  - [x] Call update endpoint
  - [x] Handle success/error
- [x] 6. Implement useDeleteTemplate hook:
  - [x] Accept template ID
  - [x] Call delete endpoint
  - [x] Handle success/error

### Template Form Component
- [x] 7. Create src/components/Templates/TemplateForm.tsx
- [x] 8. Add template name input field
- [x] 9. Add letterhead text textarea
- [x] 10. Add opening paragraph textarea
- [x] 11. Add closing paragraph textarea
- [x] 12. Add sections management:
  - [x] List of section names
  - [x] Add section button
  - [x] Remove section button
  - [x] Reorder sections (drag-drop or buttons)
- [x] 13. Add "Set as Default" checkbox
- [x] 14. Add form validation
- [x] 15. Add save button with loading state
- [x] 16. Add cancel button
- [x] 17. Handle create vs edit mode
- [x] 18. Pre-fill form in edit mode

### Template Display Components
- [x] 19. Create src/components/Templates/TemplateCard.tsx
- [x] 20. Display template name
- [x] 21. Display "Default" badge if is_default
- [x] 22. Display section count
- [x] 23. Display created date
- [x] 24. Add edit button
- [x] 25. Add delete button
- [x] 26. Add delete confirmation dialog
- [x] 27. Create src/components/Templates/TemplateList.tsx
- [x] 28. Render grid/list of TemplateCards
- [x] 29. Add empty state
- [x] 30. Add loading skeleton

### Template Management Page
- [x] 31. Create src/pages/TemplateManagement.tsx
- [x] 32. Add page header with title
- [x] 33. Add "Create Template" button
- [x] 34. Show TemplateForm in dialog on create
- [x] 35. Render TemplateList component
- [x] 36. Handle edit: open dialog with TemplateForm pre-filled
- [x] 37. Handle delete with confirmation
- [x] 38. Add loading state
- [x] 39. Add error state
- [x] 40. Refresh list after create/update/delete

---

## PR #18: Create Letter Page - Frontend

### Letter Generation API Hooks
- [x] 1. Create src/hooks/useLetterGeneration.ts
- [x] 2. Implement useGenerateLetter hook:
  - [x] Accept template ID and document IDs
  - [x] Call generate endpoint
  - [x] Handle loading state (can take up to 30s)
  - [x] Handle success/error
  - [x] Return generated letter data

### Document Selection Component
- [x] 3. Create src/components/CreateLetter/DocumentSelector.tsx
- [x] 4. Fetch and display available documents
- [x] 5. Add checkbox for each document
- [x] 6. Enforce max selection of 5 documents:
  - [x] Disable checkboxes when 5 selected
  - [x] Show message "Maximum 5 documents"
- [x] 7. Display selected count (e.g., "3 of 5 selected")
- [x] 8. Add search/filter for documents
- [x] 9. Show document metadata (name, date, size)
- [x] 10. Add "Clear Selection" button

### Template Selection Component
- [x] 11. Create src/components/CreateLetter/TemplateSelector.tsx
- [x] 12. Fetch and display available templates
- [x] 13. Render as dropdown/select or radio buttons
- [x] 14. Pre-select default template if exists
- [x] 15. Show template preview on selection (optional)
- [x] 16. Handle case where no templates exist

### Generation Progress Component
- [x] 17. Create src/components/CreateLetter/GenerationProgress.tsx
- [x] 18. Show loading spinner during generation
- [x] 19. Show progress message "Generating your demand letter..."
- [x] 20. Show estimated time remaining (optional)
- [x] 21. Add cancel button (optional, if API supports)

### Create Letter Page
- [x] 22. Create src/pages/CreateLetter.tsx
- [x] 23. Add page header with title and description
- [x] 24. Add optional title input for letter
- [x] 25. Render TemplateSelector component
- [x] 26. Render DocumentSelector component
- [x] 27. Add "Generate Letter" button:
  - [x] Disabled if template or documents not selected
  - [x] Disabled if < 1 or > 5 documents selected
- [x] 28. Show GenerationProgress when generating
- [x] 29. On success, redirect to /letters/:id/finalize
- [x] 30. On error, show error message with retry option
- [x] 31. Add form validation and error states
- [x] 32. Add helpful messages/tooltips

---

## PR #19: Finalize Letter Page - Frontend

### Letter Display Component
- [x] 1. Create src/components/Letters/LetterViewer.tsx
- [x] 2. Accept content prop (HTML string)
- [x] 3. Render HTML content safely using react-markdown or dangerouslySetInnerHTML with sanitization
- [x] 4. Apply proper styling to rendered HTML
- [x] 5. Add formatting for:
  - [x] Headings
  - [x] Paragraphs
  - [x] Bold/italic text
  - [x] Lists
- [x] 6. Make scrollable if content is long
- [x] 7. Add print-friendly styles

### Letter Editor Component
- [x] 8. Create src/components/Letters/LetterEditor.tsx
- [x] 9. Accept content prop and onChange callback
- [x] 10. Use rich text editor or large textarea
- [x] 11. Preserve HTML formatting in edit mode
- [x] 12. Add basic formatting toolbar (optional):
  - [x] Bold, italic
  - [x] Headings
  - [x] Lists
- [x] 13. Add character/word count (optional)
- [x] 14. Auto-save draft functionality (optional)

### Finalize Letter API Hooks
- [x] 15. Create src/hooks/useLetterFinalize.ts
- [x] 16. Implement useUpdateLetter hook:
  - [x] Accept letter ID and updated content
  - [x] Call update endpoint
  - [x] Handle success/error
- [x] 17. Implement useFinalizeLetter hook:
  - [x] Accept letter ID
  - [x] Call finalize endpoint
  - [x] Handle loading (docx generation)
  - [x] Handle success/error
  - [x] Return download URL

### Finalize Letter Page
- [x] 18. Create src/pages/FinalizeLetter.tsx
- [x] 19. Fetch letter by ID from URL params
- [x] 20. Add page header with letter title
- [x] 21. Add "Edit" button (top right)
- [x] 22. Add "Save" button (top right, visible in edit mode)
- [x] 23. Add "Finalize" button (bottom right)
- [x] 24. Implement view mode:
  - [x] Show LetterViewer component
  - [x] "Edit" button visible
- [x] 25. Implement edit mode:
  - [x] Show LetterEditor component
  - [x] "Save" button visible
  - [x] "Edit" button hidden
- [x] 26. Handle save action:
  - [x] Call useUpdateLetter hook
  - [x] Show success message
  - [x] Switch back to view mode
  - [x] Handle errors
- [x] 27. Handle finalize action:
  - [x] Show confirmation dialog
  - [x] Call useFinalizeLetter hook
  - [x] Show loading state during docx generation
  - [x] On success, redirect to /letters
  - [x] Show success message with download link
  - [x] Handle errors
- [x] 28. Add loading state while fetching letter
- [x] 29. Handle case where letter doesn't exist
- [x] 30. Handle case where letter is already finalized (redirect to edit page)

---

## PR #20: Generated Letters Library Page - Frontend

### Letter List API Hooks
- [x] 1. Create src/hooks/useLetters.ts
- [x] 2. Implement useLetters hook:
  - [x] Fetch letters list
  - [x] Accept sorting params
  - [x] Accept filter params (status)
  - [x] Handle pagination
  - [x] Handle loading/error
- [x] 3. Implement useDeleteLetter hook:
  - [x] Accept letter ID
  - [x] Call delete endpoint
  - [x] Handle success/error
- [x] 4. Implement useExportLetter hook:
  - [x] Accept letter ID
  - [x] Call export endpoint
  - [x] Return download URL
  - [x] Handle errors

### Letter Card Component
- [x] 5. Create src/components/Letters/LetterCard.tsx
- [x] 6. Display letter title
- [x] 7. Display status badge:
  - [x] "Draft" badge for draft status
  - [x] No badge for created status
- [x] 8. Display created date
- [x] 9. Display last modified date
- [x] 10. Display template name (if available)
- [x] 11. Add "Edit" button
- [x] 12. Add "Download" button (if finalized)
- [x] 13. Add "Delete" button with confirmation
- [x] 14. Add click handler to open edit page
- [x] 15. Add hover effects

### Letter List Component
- [x] 16. Create src/components/Letters/LetterList.tsx
- [x] 17. Render grid or list of LetterCards
- [x] 18. Add sorting controls:
  - [x] Sort by date created
  - [x] Sort by date modified
  - [x] Sort by title
  - [x] Sort by status
- [x] 19. Add filter controls:
  - [x] Filter by status (all, draft, created)
- [x] 20. Add search functionality
- [x] 21. Add empty state when no letters
- [x] 22. Add loading skeleton
- [x] 23. Implement pagination if needed

### Generated Letters Page
- [x] 24. Create src/pages/GeneratedLetters.tsx
- [x] 25. Add page header with title
- [x] 26. Add "Create New Letter" button (links to /create-letter)
- [x] 27. Render sorting and filter controls
- [x] 28. Render LetterList component
- [x] 29. Handle edit: navigate to /letters/:id/edit
- [x] 30. Handle download: trigger file download
- [x] 31. Handle delete with confirmation dialog
- [x] 32. Add loading state
- [x] 33. Add error state
- [x] 34. Refresh list after delete

---

## PR #21: Edit Letter Page - Frontend

### Edit Letter Page
- [x] 1. Create src/pages/EditLetter.tsx
- [x] 2. Fetch letter by ID from URL params
- [x] 3. Verify letter exists
- [x] 4. Add page header with letter title
- [x] 5. Add back button to return to letters library
- [x] 6. Add "Edit" button (top right)
- [x] 7. Add "Save" button (top right, visible in edit mode)
- [x] 8. Add "Re-export" button (if letter is finalized)
- [x] 9. Add "Download" button (if docx exists)
- [x] 10. Implement view mode:
  - [x] Show LetterViewer component (reuse from PR #19)
  - [x] "Edit" button visible
  - [x] Download button visible if docx exists
- [x] 11. Implement edit mode:
  - [x] Show LetterEditor component (reuse from PR #19)
  - [x] "Save" button visible
  - [x] "Edit" button hidden
- [x] 12. Handle save action:
  - [x] Call useUpdateLetter hook
  - [x] Show success message
  - [x] Switch back to view mode
  - [x] Update letter data
  - [x] Handle errors
- [x] 13. Handle re-export action:
  - [x] Show confirmation dialog
  - [x] Call useExportLetter hook
  - [x] Show loading state
  - [x] On success, update download URL
  - [x] Show success message
  - [x] Handle errors
- [x] 14. Handle download action:
  - [x] Trigger browser download using download URL
- [x] 15. Add loading state while fetching letter
- [x] 16. Handle case where letter doesn't exist (404)
- [x] 17. Add unsaved changes warning when navigating away from edit mode
- [x] 18. Handle draft letters:
  - [x] Show "Finalize" button instead of "Re-export"
  - [x] On finalize, redirect to finalize page or show finalize flow

