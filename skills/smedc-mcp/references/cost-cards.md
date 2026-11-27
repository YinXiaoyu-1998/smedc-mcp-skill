# Cost cards: directory lookup and local CSV analysis

## Published launcher and service boundary

Launcher `0.26.0` is published and independently verified and approved for installation.
Install or update only through the core Skill's exact pinned procedure. Before cost-card use,
verify the matching service rollout and explicit tenant category configuration; publication,
installation and static discovery alone do not establish live service or tenant readiness.
The receipt workflow below requires the cutover launcher and matching service.

## Upload the original

Use the existing `upload_structured_dataset` original-file transport with `dataset: "cost_cards"`,
exact `enterpriseName` and `idempotencyKey`, after the active-admin role preflight.
Supply the unchanged original through `file: {name, mediaType, encoding: "path", filePath}` with
an absolute local `filePath`. Do not add `confidentialityLevel`, date/snapshot fields or split the
file; the configured category supplies its level. Accept XLSX or UTF-8 CSV with all 35 registered
business columns. Keep SPU/SKU/item codes as strings, including
leading zeroes. The service owns normalization and validation; the agent does not repair,
split, discard exception sheets, infer missing columns or rewrite the original.

A missing/duplicate/unknown column, damaged or hidden candidate recipe sheet, invalid field,
or conflicting repeated card/recipe field rejects the whole file. Report the returned
SPU＋SKU, recipe, field, worksheet and original row locations. Present-but-null differs from
zero and may explicitly overwrite an older value. Source flags such as “是否配置成本卡” and
“菜品是否删除”, zero quantities, duplicate items and overlapping stores do not archive a card.
Recipe type retains the source text, including `全局（标准配方）` / `特定（例外配方）`;
these examples are not an exhaustive two-value enum.

When the connected dataset registry exposes `store_name`, one organization + enterprise +
source namespace + SPU + SKU + applicable store name identifies a card. Each applicable store
gets its own card. A row listing multiple stores is included in each named store's card with its
original store text. An empty applicable-store field goes to the enterprise-wide card. Existing
unsplit cards retain their original CSVs and appear with an empty directory store. A successful
change replaces the contents of the matching identity only. Omitted identities stay unchanged.
If `store_name` is absent, the service still uses the earlier SPU/SKU identity and a separate
store upload can overwrite a same-identity card. Equal normalized content causes zero directory
writes and zero CSV replacements.
Originals and import batches remain retained. A new successful upload restores an archived card,
including identical content; replaying an old successful idempotency key does not restore it.
Use a fresh key for a genuinely new upload, never to disguise a failed validation.

Keep the returned `jobRef` of kind `row_import` and use
`query_jobs({query: {mode: "import_receipt", jobRef}})`. The receipt includes `jobRef` and the
structured import status views `document`, `processing` and `importBatch`. Follow the core
Skill's bounded polling schedule until `importBatch.status` is `applied`, `failed` or `rejected`.
An immediate acceptance or exact replay can return safe asynchronous progress. Only an `applied`
batch with current content-read permission exposes `importBatch.publicationSummary` in the receipt. It contains `inputCardCount`, `inputItemRowCount`,
`counts`, `changes`, `changesTruncated`; readable `sourceSheetSummary` remains an array.
The publication summary belongs to that committed batch. `inputItemRowCount` counts original
item rows. One original row can contribute to several store cards. `inserted`, `updated`, `unchanged`,
`restored` counts are exact; `changes` is bounded by 100 entries / 32 KiB and
`changesTruncated` marks omitted details. It contains field names, not old/new values or links.
Status rechecks current content-read permission; an admin uploader may not see content counts
or changes after loss of access. Authorized current readers of failed/rejected batches receive
returned validation locations and ignored-sheet/source-summary arrays; an owner without content
read permission receives safe progress/errorCode only. Revoked access returns 404; do not infer
hidden counts or bypass the denial. No status response grants original-file read access or exposes
raw storage keys. Do not reconstruct that batch's summary from today's directory.

## Find cards before reading details

Use registry discovery, then call `query_structured_dataset` with this argument object:

```json
{
  "dataset": "cost_cards",
  "filter": { "field": "dish_name", "op": "eq", "value": "滩羊肉锅" }
}
```

The service selects detail mode automatically; `mode` is not a request parameter.
It only queries the current authorized directory, with stable pagination
(default 50 / maximum 200 rows), registered select/filter/sort fields and a fresh permission
check per page. Filter by exact `store_name` where the registry exposes it. Use the CSV for
item, recipe, quantity and original applicable-store-list detail.

Directory fields are `cost_card_id`, `enterprise_name`, `source_namespace`, `spu_id`, `sku_id`, `store_name`,
`dish_name`, `specification_name`, `base_category_name`, `sale_price`, `has_cost_card`,
`source_dish_deleted`, `revision`, `source_document_id`, `import_batch_id`, `item_row_count`,
`recipe_count`, `byte_size`, `csv_schema_version`. `sale_price` filter/output uses an exact
non-exponent decimal string or null; JSON numbers are rejected. `revision` is a string.
Internal object keys and business hashes are not directory fields.

Name `eq`/`contains`/`starts_with` are literal controlled matches, with `%`, `_` and backslash
escaped as data; no synonym or fuzzy identity inference. For the same name, return candidates
with enterprise/source/SPU/SKU/store/specification and preserve ambiguity until the employee's scope
or evidence identifies a card. Never merge or arbitrarily pick one. Coverage describes the
current readable directory; source-document archive status does not hide active cards.
Cost-card coverage uses `accessMode: "catalog_query"`, `metadataPolicy: "none"`, `cardCount`,
`totalItemRowCount` and `sources[]` grouped by each `sourceDocumentId` + `importBatchId`, with
per-source card/item-row counts. It includes only currently authorized unarchived directory cards,
not original input totals. An optional exact `enterpriseName` narrows this readable coverage.

## Download one complete CSV per card

`download_cost_cards` accepts exactly these optional selectors:

| Selector            | Meaning                                          |
| ------------------- | ------------------------------------------------ |
| `enterpriseName`    | Exact enterprise                                 |
| `costCardIds`       | Nonempty array of explicit card IDs, at most 100 |
| `spuIds` / `skuIds` | Nonempty code arrays, each at most 100           |
| `dishName`          | Exact dish name                                  |
| `dishNameContains`  | Literal dish-name substring                      |
| `specificationName` | Exact specification                              |
| `baseCategoryName`  | Exact category                                   |

To narrow by store, query `store_name` and pass the returned `costCardIds`. A selection with
multiple cards sharing an enterprise/source/SPU/SKU requires the store-aware launcher and matching
service. With the currently approved legacy launcher, issue separate requests for those IDs.
The store-aware workspace candidate is `0.27.0`, pending publication and verification.

Different fields combine with AND; values within an array combine with OR. Omitted selectors
mean the currently authorized scope. No dates, store selectors, arbitrary API paths or SQL.
Explicit IDs must all be active and readable or the entire request fails; condition-based
selection returns only readable matches, including an explicit zero-card result. Oversized
selection fails and requires narrower scope; it never silently takes the first N cards.
The selection is flat, not nested in a `selection` property. Explicit missing/unreadable IDs reject
the entire request (403); the card-count cap returns 409 without truncating. Changed cards during
signing return retryable 409, “成本卡已变化，请重新下载”; request a fresh complete download.
A condition-based zero-card result is a successful empty manifest, not evidence of hidden data.

The launcher consumes short-lived signed URLs internally, validates full card/file counts,
identity/schema/bytes/SHA-256 and safe local paths, then returns local files and safe metadata.
The exact result is `{localDirectory, dataset: "cost_cards", cardCount, totalItemRowCount, files}`;
`files` contains only CSV basenames `cost_card_<costCardId>.csv`. These stable filenames prevent
same-name/specification files overwriting each other. `manifest.json` is inside `localDirectory`.
It contains `expiresAt`, `cardCount`, `totalItemRowCount`, `cards`; every card entry retains
`costCardId`, string `revision`, `enterpriseName`, `sourceNamespace`, `spuId`, `skuId`, `dishName`,
`specificationName`, `schemaVersion`, `itemRowCount`, `byteSize`, `checksumSha256`,
`sourceDocumentId`, `importBatchId`, plus `fileName`. Only the internal `presignedDownloadUrl`
is removed. Store-aware manifests also retain `storeName` on each entry. Zero cards returns
`files: []` and a valid empty local manifest.
The two source IDs belong to each card, never one shared batch source. They provide provenance,
not permission to fetch the original. Do not put CSV bodies, base64 or signed URLs into model context.

Delivery is UTF-8 without BOM, RFC 4180 comma quoting, LF with final newline. Each CSV has
35 business columns plus `source_sheet_index`, `source_sheet_name`, `source_row_number` = 38
columns. It is not an upload template; re-upload the retained original instead. Read codes and
numbers as strings, use exact decimal arithmetic locally, interpret percent values as ratios,
booleans as true/false, empty nullable fields as null. Preserve standard/exception recipes,
repeated item multiplicities, units and original applicable-store text. Do not derive one final
store recipe, infer replacement/addition, mix units, or sum multiple recipe costs as a card total.

`contentHash` compares normalized business content; `checksumSha256` covers exact CSV bytes.
Source rows and store-text formatting can change bytes without changing business content.
Downloads reauthorize current data independently of a prior query; a new revision is not a
historical snapshot of that query. Signing rechecks permission/state/revision/source/pointer
and rejects the whole manifest if they changed. URL TTL is at most 15 minutes. Replaced CSVs
wait at least 24 hours for garbage collection; this grace does not provide historical CSV access.

On retryable expired links the launcher may obtain one fresh manifest, first removing all
outputs of the failed attempt, then redownloading the entire batch. Never mix two manifests or
keep old A while filling new B. A second failure or permission denial ends the operation and
cleans partial output. The agent must use a `finally` block to delete only this download's
launcher-created directory after local work, including analysis failure/cancellation. Preserve
safe durable findings/provenance when needed; do not delete employee files or broad prefixes.

## Permissions and archive

Read access requires current enabled business authorization, the enterprise's group-level
`cost_cards` category grant, configured category confidentiality and an active card.
Applicable stores in recipes do not create store-level permissions. Admin management and upload
ownership do not grant directory/CSV content access. Legacy/preparing/suspended modes do not
fall back to old file rules for this dataset. Source originals have independent read/archive
rules; archiving an original leaves active card directory/CSV access unchanged.

Card archive is a current same-organization admin operation; the tool is
`archive_cost_card({costCardId})`. It hides that card from ordinary directory/CSV access,
preserves its identity and current object, and does not archive the original. A new upload can
restore it as described above. Archive accepts only the exact `costCardId`, with no business
payload, and returns `{costCardId, archived: true, revision}` with a string revision. It is not
hard deletion. Both new tools require the matching service rollout and tenant configuration;
do not bypass through HTTP if the approved launcher lacks them.

After the matching service rollout, open or refresh the fixed category list to find `cost_cards`.
New categories begin with an unset level and no default grants.
The administrator sets its level and explicit group grants through the existing UI or MCP flow.
Existing category settings, grants and organization mode are preserved by registration.
A missing category after rollout is a service migration issue for the operator.

For sales association, the companion uses `matched_product_name` first and `product_name`
only when the first is empty/unmatched. Multiple candidates retain ambiguity; no name foreign
key or server join is introduced. The service does not run Skills, generate reports or analyze recipes.
