# PromptiTron Frontend

This is the frontend for PromptiTron, built with **Next.js 15 (App Router)**, **TypeScript**, **Tailwind CSS**, and **shadcn/ui**.

It provides the web interface for interacting with the PromptiTron backend.

## Tech Stack

- Next.js 15
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## Getting Started

### 1. Move into the client directory

```bash
cd client
```

### 2. Install dependencies

Using **pnpm**:

```bash
pnpm install
```

Using **npm**:

```bash
npm install
```

### 3. Configure environment variables

Create a `.env.local` file inside the `client` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Replace the value with your actual backend URL if needed.

### 4. Start the development server

Using **pnpm**:

```bash
pnpm dev
```

Using **npm**:

```bash
npm run dev
```

The frontend will typically run at:

```text
http://localhost:3000
```

## Notes

- Make sure the backend API is running before testing frontend features.
- The frontend expects the backend base URL through `NEXT_PUBLIC_API_URL`.
- If the backend URL changes, update `.env.local` accordingly.
