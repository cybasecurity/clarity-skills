# Clarity cost formulas by schedule

<!-- generated-reference -->

Delegations (`Costs5` → `Costs4` → `Costs3`) are resolved, so each cell is the effective formula. `n` is whatever the charge site passes (serialized bytes, list length, argument count, contract size): read the call site before estimating. This is source extraction, not a measurement. From epoch 4.0 the active schedule is native Rust (historical boot cost contracts remain callable) and SIP-006 cost voting is disabled (SIP-044), so schedules change only by hard fork.

Schedule selection (`default_cost_contract_for_epoch` in `clarity/src/vm/costs/mod.rs`):

```rust
fn default_cost_contract_for_epoch(epoch_id: StacksEpochId) -> Result<String, CostErrors> {
        let result = match epoch_id {
            StacksEpochId::Epoch10 => {
                return Err(CostErrors::Expect("Attempted to get default cost functions for Epoch 1.0 where Clarity does not exist".into()));
            }
            StacksEpochId::Epoch20 => COSTS_1_NAME.to_string(),
            StacksEpochId::Epoch2_05 => COSTS_2_NAME.to_string(),
            StacksEpochId::Epoch21
            | StacksEpochId::Epoch22
            | StacksEpochId::Epoch23
            | StacksEpochId::Epoch24
            | StacksEpochId::Epoch25
            | StacksEpochId::Epoch30
            | StacksEpochId::Epoch31
            | StacksEpochId::Epoch32 => COSTS_3_NAME.to_string(),
            StacksEpochId::Epoch33 | StacksEpochId::Epoch34 => COSTS_4_NAME.to_string(),
            StacksEpochId::Epoch40 | StacksEpochId::Epoch41 => COSTS_5_NAME.to_string(),
        };
        Ok(result)
    }
```

Block budget (verify with `GET /v2/pox` → `epochs[].block_limit`): runtime 5,000,000,000; reads 15,000 (30,000 from epoch 4.0); read bytes 100,000,000 (200,000,000 from 4.0); writes 15,000; write bytes 15,000,000.

| Cost function | Clarity | costs_3 (Epoch 2.1–3.2) | costs_4 (Epoch 3.3–3.4) | costs_5 (Epoch 4.0+) |
|---|---|---|---|---|
| `cost_add` | + | runtime 11·n + 125 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_analysis_bind_name` |  | runtime n + 59 | = previous | = previous |
| `cost_analysis_check_let` |  | runtime n + 10 | = previous | = previous |
| `cost_analysis_check_tuple_cons` |  | runtime 3·n·log2(n) + 5 | = previous | = previous |
| `cost_analysis_check_tuple_get` |  | runtime log2(n) + 2 | = previous | = previous |
| `cost_analysis_check_tuple_merge` |  | runtime 45·n·log2(n) + 49 | = previous | = previous |
| `cost_analysis_fetch_contract_entry` |  | runtime n + 1516; reads 1; read bytes n + 1 | = previous | = previous |
| `cost_analysis_get_function_entry` |  | runtime 78·n + 1307; reads 1; read bytes n + 1 | = previous | = previous |
| `cost_analysis_iterable_func` |  | runtime 2·n + 14 | = previous | = previous |
| `cost_analysis_list_items_check` |  | runtime 2·n + 4 | = previous | = previous |
| `cost_analysis_lookup_function` |  | runtime 18 | = previous | = previous |
| `cost_analysis_lookup_function_types` |  | runtime n + 26 | = previous | = previous |
| `cost_analysis_lookup_variable_const` |  | runtime 15 | = previous | = previous |
| `cost_analysis_lookup_variable_depth` |  | runtime n·log2(n) + 12 | = previous | = previous |
| `cost_analysis_option_check` |  | runtime 4 | = previous | = previous |
| `cost_analysis_option_cons` |  | runtime 5 | = previous | = previous |
| `cost_analysis_storage` |  | runtime 2·n + 94; reads 1; read bytes 1; writes 1; write bytes n + 1 | = previous | = previous |
| `cost_analysis_tuple_items_check` |  | runtime n + 28 | = previous | = previous |
| `cost_analysis_type_annotate` |  | runtime n + 9 | = previous | = previous |
| `cost_analysis_type_check` | deploy: type checking | runtime 113·n + 1 | = previous | = previous |
| `cost_analysis_type_lookup` |  | runtime n + 4 | = previous | = previous |
| `cost_analysis_use_trait_entry` |  | runtime 9·n + 698; reads 1; read bytes n + 1; write bytes n + 1 | = previous | = previous |
| `cost_analysis_visit` |  | runtime 1 | = previous | = previous |
| `cost_and` |  | runtime 3·n + 120 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_append` | append | runtime 73·n + 285 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_as_contract` | as-contract | runtime 138 | = previous | = previous |
| `cost_as_contract_safe` |  | not available | runtime 125·n + 888 | = previous |
| `cost_as_max_len` | as-max-len? | runtime 475 | = previous | runtime 31 |
| `cost_asserts` |  | runtime 128 | = previous | = previous |
| `cost_ast_cycle_detection` |  | runtime 141·n + 72 | = previous | = previous |
| `cost_ast_parse` | deploy: parsing | runtime 27·n + 81 | = previous | = previous |
| `cost_at_block` |  | runtime 1327; reads 1; read bytes 1 | = previous | = previous |
| `cost_begin` |  | runtime 151 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_bind_name` |  | runtime 216 | = previous | = previous |
| `cost_bitwise_and` |  | runtime 15·n + 129 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_bitwise_left_shift` |  | runtime 167 | = previous | runtime 31 |
| `cost_bitwise_not` |  | runtime 147 | = previous | runtime 31 |
| `cost_bitwise_or` |  | runtime 15·n + 129 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_bitwise_right_shift` |  | runtime 167 | = previous | runtime 31 |
| `cost_block_info` | get-block-info? | runtime 6321; reads 1; read bytes 1 | = previous | = previous |
| `cost_buff_to_int_be` |  | runtime 141 | = previous | runtime 31 |
| `cost_buff_to_int_le` |  | runtime 141 | = previous | runtime 31 |
| `cost_buff_to_uint_be` |  | runtime 141 | = previous | runtime 31 |
| `cost_buff_to_uint_le` |  | runtime 141 | = previous | runtime 31 |
| `cost_burn_block_info` |  | runtime 96479; reads 1; read bytes 1 | = previous | = previous |
| `cost_concat` | concat | runtime 37·n + 220 | = previous | runtime ⌊n/1024⌋ + 31 |
| `cost_contract_call` | contract-call? | runtime 134 | = previous | = previous |
| `cost_contract_hash` |  | not available | runtime 188; reads 1; read bytes 32 | = previous |
| `cost_contract_of` |  | runtime 13400 | = previous | = previous |
| `cost_contract_storage` | deploy: storing contract | runtime 11·n + 7165; writes 1; write bytes n + 1 | = previous | = previous |
| `cost_create_ft` |  | runtime 1831; writes 2; write bytes 1 | = previous | = previous |
| `cost_create_map` |  | runtime n + 1564; writes 1; write bytes n + 1 | = previous | = previous |
| `cost_create_nft` |  | runtime n + 1570; writes 1; write bytes n + 1 | = previous | = previous |
| `cost_create_var` |  | runtime 7·n + 2025; writes 2; write bytes n + 1 | = previous | = previous |
| `cost_default_to` |  | runtime 268 | = previous | runtime 31 |
| `cost_div` | / | runtime 13·n + 125 | = previous | runtime ⌊n/32⌋ + 32 |
| `cost_ed25519verify` |  | not available | = previous | runtime ⌊n/512⌋ + 39 |
| `cost_element_at` |  | runtime 498 | = previous | runtime 31 |
| `cost_eq` |  | runtime 7·n + 151 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_err_cons` |  | runtime 199 | = previous | runtime 31 |
| `cost_fetch_entry` | map-get? | runtime n + 1025; reads 1; read bytes n + 1 | = previous | runtime 44; reads 1; read bytes n + 1 |
| `cost_fetch_var` | var-get | runtime n + 468; reads 1; read bytes n + 1 | = previous | runtime 2·⌊n/512⌋ + 44; reads 1; read bytes n + 1 |
| `cost_filter` | filter | runtime 407 | = previous | runtime ⌊n/4⌋ + 32 |
| `cost_fold` | fold | runtime 460 | = previous | runtime ⌊n/8⌋ + 32 |
| `cost_from_consensus_buff` | from-consensus-buff? | runtime 3·n·log2(n) + 185 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_ft_balance` | ft-get-balance | runtime 479; reads 1; read bytes 1 | = previous | = previous |
| `cost_ft_burn` | ft-burn? | runtime 549; reads 2; read bytes 1; writes 2; write bytes 1 | = previous | = previous |
| `cost_ft_get_supply` |  | runtime 420; reads 1; read bytes 1 | = previous | = previous |
| `cost_ft_mint` | ft-mint? | runtime 1479; reads 2; read bytes 1; writes 2; write bytes 1 | = previous | = previous |
| `cost_ft_transfer` | ft-transfer? | runtime 549; reads 2; read bytes 1; writes 2; write bytes 1 | = previous | = previous |
| `cost_ge` |  | runtime 7·n + 128 | = previous | runtime ⌊n/256⌋ + 38 |
| `cost_geq` |  | runtime 7·n + 128 | = previous | runtime ⌊n/256⌋ + 38 |
| `cost_get_bitcoin_tx_output` |  | not available | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_hash160` |  | runtime n + 188 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_if` | if | runtime 168 | = previous | = previous |
| `cost_index_of` |  | runtime n + 211 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_inner_type_check_cost` | argument type checks | runtime 2·n + 5 | = previous | = previous |
| `cost_int_cast` |  | runtime 135 | = previous | runtime 31 |
| `cost_int_to_ascii` |  | runtime 147 | = previous | runtime 31 |
| `cost_int_to_utf8` |  | runtime 181 | = previous | runtime 31 |
| `cost_is_err` |  | runtime 245 | = previous | runtime 31 |
| `cost_is_none` |  | runtime 214 | = previous | runtime 31 |
| `cost_is_okay` |  | runtime 258 | = previous | runtime 31 |
| `cost_is_some` |  | runtime 195 | = previous | runtime 31 |
| `cost_is_standard` |  | runtime 127 | = previous | runtime 31 |
| `cost_keccak256` | keccak256 | runtime n + 127 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_le` |  | runtime 7·n + 128 | = previous | runtime ⌊n/256⌋ + 38 |
| `cost_len` |  | runtime 429 | = previous | runtime 31 |
| `cost_leq` |  | runtime 7·n + 128 | = previous | runtime ⌊n/256⌋ + 38 |
| `cost_let` | let | runtime 117·n + 178 | = previous | runtime ⌊n/8⌋ + 32 |
| `cost_list_cons` |  | runtime 14·n + 164 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_load_contract` | loading a called contract | runtime n + 80; reads 3; read bytes n + 1 | = previous | = previous |
| `cost_log2` |  | runtime 133 | = previous | runtime 31 |
| `cost_lookup_function` |  | runtime 16 | = previous | = previous |
| `cost_lookup_variable_depth` | variable lookup | runtime n + 1 | = previous | = previous |
| `cost_lookup_variable_size` |  | runtime 2·n + 1 | = previous | = previous |
| `cost_map` | map | runtime 1198·n + 3067 | = previous | runtime ⌊n/4⌋ + 32 |
| `cost_match` |  | runtime 264 | = previous | runtime 31 |
| `cost_mod` |  | runtime 141 | = previous | runtime 31 |
| `cost_mul` | * | runtime 13·n + 125 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_nft_burn` |  | runtime 9·n + 572; reads 1; read bytes 1; writes 1; write bytes 1 | = previous | = previous |
| `cost_nft_mint` | nft-mint? | runtime 9·n + 575; reads 1; read bytes 1; writes 1; write bytes 1 | = previous | = previous |
| `cost_nft_owner` | nft-get-owner? | runtime 9·n + 795; reads 1; read bytes 1 | = previous | = previous |
| `cost_nft_transfer` | nft-transfer? | runtime 9·n + 572; reads 1; read bytes 1; writes 1; write bytes 1 | = previous | = previous |
| `cost_not` |  | runtime 138 | = previous | runtime 31 |
| `cost_ok_cons` |  | runtime 199 | = previous | runtime 31 |
| `cost_or` |  | runtime 3·n + 120 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_pow` |  | runtime 143 | = previous | runtime 31 |
| `cost_principal_construct` |  | runtime 398 | = previous | runtime 32 |
| `cost_principal_destruct` |  | runtime 314 | = previous | runtime 32 |
| `cost_principal_of` |  | runtime 984 | = previous | = previous |
| `cost_print` | print | runtime 15·n + 1458 | = previous | runtime ⌊n/512⌋ + 31 |
| `cost_replace_at` |  | runtime n + 561 | = previous | runtime ⌊n/512⌋ + 31 |
| `cost_restrict_assets` |  | not available | runtime 125·n + 750 | = previous |
| `cost_secp256k1decompress` |  | not available | = previous | runtime 39 |
| `cost_secp256k1recover` | secp256k1-recover? | runtime 8655 | = previous | runtime 38 |
| `cost_secp256k1verify` | secp256k1-verify | runtime 8349 | = previous | runtime 38 |
| `cost_secp256r1verify` |  | not available | runtime 51750 | runtime 38 |
| `cost_set_entry` | map-set / map-insert / map-delete | runtime 4·n + 1899; reads 1; writes 1; write bytes n + 1 | = previous | runtime 3·⌊n/512⌋ + 45; reads 1; writes 1; write bytes n + 1 |
| `cost_set_var` | var-set | runtime 5·n + 655; reads 1; writes 1; write bytes n + 1 | = previous | runtime 4·⌊n/512⌋ + 45; reads 1; writes 1; write bytes n + 1 |
| `cost_sha256` | sha256 | runtime n + 100 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_sha512` |  | runtime n + 176 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_sha512t256` |  | runtime n + 56 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_slice` |  | runtime 448 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_some_cons` |  | runtime 199 | = previous | runtime 31 |
| `cost_sqrti` |  | runtime 142 | = previous | runtime 31 |
| `cost_string_to_int` |  | runtime 168 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_string_to_uint` |  | runtime 168 | = previous | runtime ⌊n/16⌋ + 31 |
| `cost_stx_account` |  | runtime 4654; reads 1; read bytes 1 | = previous | = previous |
| `cost_stx_balance` | stx-get-balance | runtime 4294; reads 1; read bytes 1 | = previous | = previous |
| `cost_stx_transfer` | stx-transfer? | runtime 4640; reads 1; read bytes 1; writes 1; write bytes 1 | = previous | = previous |
| `cost_stx_transfer_memo` |  | runtime 4709; reads 1; read bytes 1; writes 1; write bytes 1 | = previous | = previous |
| `cost_sub` |  | runtime 11·n + 125 | = previous | runtime ⌊n/32⌋ + 32 |
| `cost_to_ascii` |  | not available | runtime 16·n + 150 | runtime ⌊n/64⌋ + 32 |
| `cost_to_consensus_buff` | to-consensus-buff? | runtime n + 233 | = previous | runtime ⌊n/512⌋ + 38 |
| `cost_try_ret` |  | runtime 240 | = previous | runtime 31 |
| `cost_tuple_cons` | tuple literal | runtime 10·n·log2(n) + 1876 | = previous | runtime ⌊n/4⌋ + 31 |
| `cost_tuple_get` | get | runtime 4·n·log2(n) + 1736 | = previous | runtime ⌊n/4⌋ + 32 |
| `cost_tuple_merge` | merge | runtime 4·n + 408 | = previous | runtime ⌊n/4⌋ + 32 |
| `cost_type_parse_step` |  | runtime 4 | = previous | = previous |
| `cost_unwrap` |  | runtime 252 | = previous | runtime 31 |
| `cost_unwrap_err` |  | runtime 248 | = previous | runtime 31 |
| `cost_unwrap_err_or_ret` |  | runtime 302 | = previous | runtime 31 |
| `cost_unwrap_ret` |  | runtime 274 | = previous | runtime 31 |
| `cost_user_function_application` | calling a define-private/public | runtime 26·n + 5 | = previous | = previous |
| `cost_verify_merkle_proof` |  | not available | = previous | runtime ⌊n/4⌋ + 38 |
| `cost_xor` |  | runtime 15·n + 129 | = previous | runtime ⌊n/16⌋ + 31 |
