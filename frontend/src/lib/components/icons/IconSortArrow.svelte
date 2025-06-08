<script lang="ts">
  export let direction: "asc" | "desc" = "asc";
  export let size = "1em"; // h-4 w-4
  export let strokeWidth = 2;
  // biome-ignore lint/style/useConst: Let for Svelte prop
  let klass = "";
  export { klass as class };

  const paths = {
    asc: "M5 15l7-7 7 7",
    desc: "M19 9l-7 7-7-7",
  };
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  fill="none"
  viewBox="0 0 24 24"
  stroke="currentColor"
  stroke-width={strokeWidth}
  class={klass}
  aria-hidden="true"
>
  <path stroke-linecap="round" stroke-linejoin="round" d={paths[direction]} />
</svg>
