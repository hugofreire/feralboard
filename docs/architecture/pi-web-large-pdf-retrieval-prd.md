# PRD: pi-web Large PDF Retrieval Pipeline for Agent Chat

## Summary

`apps/pi-web` currently lets users attach files to the agent chat. For PDFs, the server extracts text and exposes the extracted file path to the agent. This works for small documents, but it does not scale well for large PDFs because the agent can end up operating on too much raw text at once.

This PRD defines a large-document pipeline for PDFs with more than 30 pages. The core idea is:

- keep the full parsing and storage on the server
- avoid sending the full extracted text into chat context
- give the agent a retrieval-oriented workflow instead

The result should be lower context usage, more reliable document analysis, and better behavior on long manuals, specs, and reports.

## Problem

The current file upload flow is acceptable for small PDFs, but large PDFs create three problems:

1. Context bloat
Large extracted text can overwhelm the model context window or waste tokens on irrelevant sections.

2. Poor navigation
The agent has no structured way to inspect large documents incrementally. It may read too much or the wrong parts first.

3. Weak UX for long documents
Users need confidence that a dropped PDF is being processed carefully, not blindly pasted into the conversation.

## Goal

Support drag-and-drop and attachment of large PDFs in `pi-web` chat while keeping the document server-side and guiding the agent to explore it carefully through retrieval.

## Non-Goals

- Full OCR pipeline for scanned image PDFs in the first version
- Vector embeddings or external search infrastructure in the first version
- Multi-user document permissions beyond the current local-Pi usage model
- General document management productization outside the chat workflow

## User Story

As a developer using `pi-web`, I want to drop a large PDF into the chat and ask questions about it without flooding the conversation with the full document text, so the agent can inspect the document carefully and answer with the relevant sections only.

## Product Requirements

### 1. Page-count threshold

When a PDF is uploaded:

- if `pages <= 30`, use the current small-document flow
- if `pages > 30`, switch to the large-document retrieval flow

The threshold should be configurable in code.

### 2. Server-side document package

For large PDFs, the server should generate and persist:

- original PDF file
- extracted text split by page
- chunked text representation for retrieval
- manifest JSON containing:
  - document id
  - original filename
  - page count
  - chunk count
  - storage paths
  - extraction status
  - optional section or heading metadata if available

### 3. Retrieval-first agent workflow

For large PDFs, the chat prompt should not include the extracted document text.

Instead, the agent should receive:

- a compact document manifest summary
- the document id
- instructions to inspect the manifest first
- instructions to search before reading large spans
- instructions to read only the relevant pages or chunks

### 4. Retrieval endpoints

The server should expose endpoints for document exploration. Initial examples:

- `GET /api/documents`
- `GET /api/documents/:id/manifest`
- `GET /api/documents/:id/pages?page=...`
- `GET /api/documents/:id/search?q=...`
- `GET /api/documents/:id/chunks?ids=...`

These endpoints should be enough to support both UI inspection and agent-side retrieval.

### 5. Agent tooling

The preferred implementation is to expose one or more custom agent tools for document retrieval, for example:

- `document_manifest`
- `document_search`
- `document_read_pages`
- `document_read_chunks`

This is better than forcing the model to manually inspect raw files because it gives the agent a narrower, cheaper retrieval path.

### 6. UI states in pi-web chat

When a large PDF is attached, the UI should show that it was indexed server-side rather than fully inserted into context.

Suggested badge states:

- `Large PDF`
- `Indexed on server`
- `Pages: N`

Optional quick actions:

- `Open manifest`
- `Preview pages`
- `Search document`

### 7. Failure handling

If extraction fails:

- preserve the uploaded PDF
- mark the document as failed in the manifest
- show the failure in the attachment UI
- still let the agent know the raw file exists, but clearly indicate that structured retrieval is unavailable

## UX Notes

The UX should communicate a different mode for large PDFs:

- user drops a PDF
- if the PDF is large, the UI should indicate that the document is being indexed
- the final attachment state should make clear that the agent will retrieve sections on demand

This should feel deliberate and safer than the small-PDF flow.

## Technical Approach

### Upload pipeline

1. User uploads or drags a PDF into `pi-web` chat.
2. Server inspects page count during upload handling.
3. If small:
   - keep current extraction behavior
4. If large:
   - create a document id
   - extract page text
   - create chunks
   - write manifest and retrieval artifacts
   - return a structured `large_document` attachment result

### Storage layout

A document storage layout should exist under a dedicated server-managed folder, for example:

```text
apps/pi-web/uploads/documents/<document-id>/
  original.pdf
  manifest.json
  pages/
    0001.txt
    0002.txt
  chunks/
    chunks.json
```

### Prompting strategy

For large PDFs, inject only something like:

```text
[Attached large document: "manual.pdf"
Document ID: doc_abc123
Pages: 184
Indexed on server.
Do not assume the full document is in context.
Read the manifest first, search for relevant sections, then read only the needed pages or chunks.]
```

### Search strategy

Initial implementation can use simple local text search over page text or chunk text.

This is enough for a first version and keeps the system simple. Embeddings can be a later improvement if needed.

## Success Criteria

- Dropping a PDF with more than 30 pages does not inject the full text into chat context
- The server stores a manifest and retrieval artifacts for large PDFs
- The agent is able to answer questions about large PDFs by retrieving specific sections
- Token usage and failure rate on large-PDF questions are lower than the naive full-text approach
- Users can see from the UI that large PDFs are handled differently

## Risks

### 1. Extraction quality

Some PDFs will have poor text extraction, broken reading order, or no text layer.

Mitigation:

- preserve page-level outputs
- expose extraction status
- treat OCR as a later phase

### 2. Over-fetching by the agent

Even with retrieval tools, the agent may still read too much.

Mitigation:

- strong tool descriptions
- explicit prompt instructions
- page and chunk limits in tool responses

### 3. Local storage growth

Large PDFs and derived artifacts can consume disk space on the Pi.

Mitigation:

- document retention policy
- optional delete action
- size reporting in document metadata

## Future Extensions

- OCR fallback for scanned PDFs
- heading extraction and automatic table-of-contents generation
- semantic search with embeddings
- document summary generation at upload time
- support for DOCX and other large document types

## Implementation Phases

### Phase 1

- page threshold detection
- manifest generation
- page and chunk storage
- retrieval endpoints
- prompt changes for large PDFs

### Phase 2

- custom agent retrieval tools
- improved UI badges and manifest preview
- better search ranking

### Phase 3

- OCR
- semantic retrieval
- summaries and section graphs

## Proposed Title for Work Tracking

`pi-web: Retrieval-first handling for large PDF chat attachments`
