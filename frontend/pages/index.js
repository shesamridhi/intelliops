// Demonstrates a basic SSR pattern: the redirect decision happens on the
// server before any HTML is sent to the client (no client-side flash).
export async function getServerSideProps() {
  return { redirect: { destination: "/login", permanent: false } };
}

export default function Home() {
  return null;
}
